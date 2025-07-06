"""
API эндпоинты для работы с платежами
"""
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
import uuid
from app.database import get_db
from app.services.auth import AuthService
from app.models import User, Tariff, Payment
from app.schemas import UserResponse, CreatePaymentRequest, CreatePaymentResponse

router = APIRouter(prefix="/payments", tags=["payments"])

async def get_current_user_dependency(request: Request, db: Session = Depends(get_db)) -> UserResponse:
    session_id = request.cookies.get("session_id")
    if not session_id:
        raise HTTPException(status_code=401, detail="Не авторизован")
    auth_service = AuthService(db)
    user = auth_service.get_user_by_session(session_id)
    if not user:
        raise HTTPException(status_code=401, detail="Сессия недействительна")
    return user

@router.post("/create", response_model=CreatePaymentResponse)
async def create_payment(
    request_data: CreatePaymentRequest,
    current_user: UserResponse = Depends(get_current_user_dependency),
    db: Session = Depends(get_db)
):
    """
    Создание платежа для выбранного тарифа
    """
    tariff = db.query(Tariff).filter(
        Tariff.tariff_id == request_data.tariff_id,
        Tariff.is_active == True
    ).first()

    if not tariff:
        raise HTTPException(status_code=404, detail="Тариф не найден или неактивен")

    # Создаем запись о платеже в нашей системе
    new_payment = Payment(
        payment_id=str(uuid.uuid4()), # Временный ID, Юкасса даст свой
        user_id=current_user.user_id,
        tariff_id=tariff.tariff_id,
        amount=tariff.price,
        currency=tariff.currency,
        minutes_added=tariff.minutes,
        # status остается 'pending' по умолчанию
    )
    db.add(new_payment)
    db.commit()
    db.refresh(new_payment)

    # Здесь должна быть логика интеграции с Юкассой:
    # 1. Отправить запрос в Юкассу на создание платежа с amount, currency, description
    # 2. Получить от Юкассы payment_id и confirmation_url
    # 3. Сохранить payment_id от Юкассы в нашей записи new_payment
    # 4. Вернуть confirmation_url клиенту для редиректа

    # ЗАГЛУШКА для демонстрации
    confirmation_url = f"https://yookassa.ru/pay/{new_payment.payment_id}" # Это не настоящая ссылка

    return CreatePaymentResponse(
        payment_id=new_payment.payment_id,
        confirmation_url=confirmation_url
    )
