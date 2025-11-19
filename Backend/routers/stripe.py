# backend/routers/stripe_router.py
import os
import stripe
from fastapi import APIRouter, Depends, HTTPException
from fastapi import Request
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from Backend.core.settings import Settings
from Backend.core.database import get_session
from Backend.models.models import User
from Backend.middleware.security import get_current_user 

router = APIRouter(prefix='/stripe', tags=['stripe'])

settings = Settings()

stripe.api_key = settings.STRIPE_SECRET_KEY
DOMAIN = 'http://localhost:8080'

router = APIRouter(prefix='/stripe', tags=['stripe'])

PLANOS = {'mensal': settings.STRIPE_PRICE_ID_MENSAL, 'anual': settings.STRIPE_PRICE_ID_ANUAL}

@router.post('/create-checkout-session/{plan_name}')
async def create_checkout_session(
    plan_name: str, 
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session)
):
    """
    Cria uma sessão de checkout do Stripe para um plano específico.
    """
    if plan_name not in PLANOS:
        raise HTTPException(status_code=400, detail='Plano inválido.')

    price_id = PLANOS[plan_name]
    
    try:
        # Busca o usuário no banco para garantir que temos os dados mais recentes
        user = await session.get(User, current_user.id)
        if not user:
            raise HTTPException(status_code=404, detail="Usuário não encontrado.")

        customer_id = user.stripe_customer_id
        # Se o usuário ainda não for um cliente no Stripe, crie um
        if not customer_id:
            customer = stripe.Customer.create(
                email=user.email,
                name=user.username,
                metadata={'user_id': str(user.id)}
            )
            customer_id = customer.id
            # Salva o ID do cliente no seu banco de dados
            user.stripe_customer_id = customer_id
            await session.commit()

        checkout_session = stripe.checkout.Session.create(
            customer=customer_id,
            payment_method_types=['card'],
            line_items=[{'price': price_id, 'quantity': 1}],
            mode='subscription', # Importante: modo de assinatura
            success_url=f'{DOMAIN}/success?session_id={{CHECKOUT_SESSION_ID}}',
            cancel_url=f'{DOMAIN}/cancel',
            metadata={
                'user_id': str(user.id) # Passa o ID do seu usuário para o webhook
            }
        )
        return {'checkout_url': checkout_session.url}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post('/webhook')
async def stripe_webhook(request: Request, session: AsyncSession = Depends(get_session)):
    """
    Recebe eventos do Stripe e atualiza o banco de dados.
    """
    payload = await request.body()
    sig_header = request.headers.get('stripe-signature')
    endpoint_secret = settings.STRIPE_WEBHOOK_SECRET
    
    event = None

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, endpoint_secret
        )
    except ValueError as e:
        print('⚠️  Error parsing payload: {}'.format(str(e)))
        raise HTTPException(status_code=400, detail="Invalid payload")
    except stripe.error.SignatureVerificationError as e:
        print('⚠️  Error verifying webhook signature: {}'.format(str(e)))
        raise HTTPException(status_code=400, detail="Invalid signature")

    # ========== CHECKOUT CONCLUÍDO ==========
    if event['type'] == 'checkout.session.completed':
        checkout_session = event['data']['object']
        
        user_id = checkout_session.get('metadata', {}).get('user_id')
        subscription_id = checkout_session.get('subscription')
        customer_id = checkout_session.get('customer')

        print(f"🔍 Checkout concluído - user_id: {user_id}")

        if not user_id:
            print("❌ user_id não encontrado nos metadados")
            return {'status': 'ignored', 'reason': 'missing user_id'}

        subscription_expires_at = None
        if subscription_id:
            try:
                subscription = stripe.Subscription.retrieve(subscription_id)
                
                # ✅ CORREÇÃO: current_period_end está dentro de items.data[0]
                if subscription.get('items') and subscription['items'].get('data'):
                    first_item = subscription['items']['data'][0]
                    current_period_end = first_item.get('current_period_end')
                    
                    if current_period_end:
                        subscription_expires_at = datetime.fromtimestamp(current_period_end)
                        print(f"✅ Data de expiração: {subscription_expires_at}")
                    else:
                        print("⚠️  current_period_end não encontrado no item")
                else:
                    print("⚠️  items.data não encontrado na subscription")
                    
            except Exception as sub_error:
                print(f"❌ Erro ao buscar subscription: {sub_error}")
                import traceback
                traceback.print_exc()

        # Atualizar usuário no banco
        try:
            user = await session.get(User, user_id)
            
            if user:
                print(f"🔍 Usuário encontrado: {user.username}")
                
                user.subscription_active = True
                user.subscription_expires_at = subscription_expires_at
                user.stripe_subscription_id = subscription_id
                user.stripe_customer_id = customer_id
                
                await session.commit()
                await session.refresh(user)
                
                print(f"✅ Assinatura ATIVADA")
                print(f"   - subscription_active: {user.subscription_active}")
                print(f"   - subscription_expires_at: {user.subscription_expires_at}")
                print(f"   - stripe_customer_id: {user.stripe_customer_id}")
                print(f"   - stripe_subscription_id: {user.stripe_subscription_id}")
            else:
                print(f"❌ Usuário {user_id} não encontrado no banco")
                
        except Exception as db_error:
            print(f"❌ Erro ao atualizar banco: {db_error}")
            import traceback
            traceback.print_exc()

    # ========== ASSINATURA ATUALIZADA ==========
    elif event['type'] == 'customer.subscription.updated':
        subscription = event['data']['object']
        customer_id = subscription.get('customer')
        subscription_status = subscription.get('status')
        
        print(f"🔄 Subscription atualizada - customer: {customer_id}, status: {subscription_status}")
        
        stmt = select(User).where(User.stripe_customer_id == customer_id)
        result = await session.execute(stmt)
        user = result.scalar_one_or_none()

        if user:
            user.subscription_active = (subscription_status == 'active')
            
            # ✅ CORREÇÃO: pegar current_period_end de items.data[0]
            if subscription.get('items') and subscription['items'].get('data'):
                first_item = subscription['items']['data'][0]
                current_period_end = first_item.get('current_period_end')
                
                if current_period_end:
                    user.subscription_expires_at = datetime.fromtimestamp(current_period_end)
            
            await session.commit()
            
            print(f"✅ Assinatura ATUALIZADA")
            print(f"   - subscription_active: {user.subscription_active}")
            print(f"   - subscription_expires_at: {user.subscription_expires_at}")
        else:
            print(f"⚠️  Customer {customer_id} não encontrado no banco")

    # ========== ASSINATURA CANCELADA ==========
    elif event['type'] == 'customer.subscription.deleted':
        subscription = event['data']['object']
        customer_id = subscription.get('customer')
        
        print(f"🗑️  Subscription cancelada - customer: {customer_id}")
        
        stmt = select(User).where(User.stripe_customer_id == customer_id)
        result = await session.execute(stmt)
        user = result.scalar_one_or_none()

        if user:
            user.subscription_active = False
            await session.commit()
            print(f"✅ Assinatura DESATIVADA para usuário {user.id}")
        else:
            print(f"⚠️  Customer {customer_id} não encontrado no banco")

    return {'status': 'success'}