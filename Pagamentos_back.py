from tkinter import filedialog
import requests
import qrcode
import uuid
import time
import datetime

def payment():
    url_create = "https://api.mercadopago.com/v1/payments"
    access_token = "APP_USR-2228715900888505-031210-e1b04741fa3a0e00fa0f3ce6e9f95306-124591658"

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
        # Esse cara aqui gera ID unico para cada reuisição, ou seja, reflete e cada QRcode gerado como unico por execução
        "X-Idempotency-Key": str(uuid.uuid4()),
    }

    data = {
        # Aqui é o valor da doação em float, 0,5 é R$0.50 e por ai vai, caso nao tenha entendido, volte para 1ª serie.
        "transaction_amount": {valor_txt.value},
        "description": "Produto Exemplo",
        "payment_method_id": "pix",
        "payer": {
            "email": "email_do_comprador@dominio.com"
        }
    }

    response = requests.post(url_create, headers=headers, json=data)
    payment = response.json()

    # Vendo se foi criado o pagamento né
    if 'id' in payment:
        payment_id = payment['id']
        print(f"Pagamento criado com ID: {payment_id}")

        # Coleta a URL para o QRcode
        qr_code_url = payment.get('point_of_interaction', {}).get(
            'transaction_data', {}).get('qr_code', '')
        if qr_code_url:
            print(f"QR Code URL: {qr_code_url}")

            # Cria o QR Code
            qr = qrcode.QRCode(
                version=1,
                error_correction=1,
                box_size=10,
                border=2,
            )
            qr.add_data(qr_code_url)
            qr.make(fit=True)

            img = qr.make_image(fill='black', back_color='white')

            # ABRE A BUCEEEET@ DA IMAGEM, AAAAHHHHHHHHHHHHHHHHHH  -By: Dilera
            img.show()
        else:
            print("QR Code não encontrado na resposta.")
    else:
        print("Erro ao criar pagamento:", payment)


    # Aqui verifica o status do pagamento
    def check_payment_status(payment_id):
        url_status = f"https://api.mercadopago.com/v1/payments/{payment_id}"
        response = requests.get(url_status, headers=headers)
        payment_status = response.json()
        return payment_status.get('status')


    # Aqui nóis salva o log da transação e seu status, isso vai servir para futuras consultas no app do Mercado Pago

    def salvar_log_transfer():
        path = filedialog.asksaveasfilename(
            title='Salvar',confirmoverwrite=True,
            defaultextension='.txt',
            filetypes=[('Arquivo de Texto', '*.txt')],
            initialfile=f'Transacao - {payment_id}.txt'
            )
        if path:
            with open(path, 'w') as transfer:
                transfer.write(f"Status do pagamento: {payment_id}\n".upper())
                transfer.write(f"Quando foi gerado o QR Code: {datetime.datetime.today().strftime('%d/%m/%Y - %H:%M')}\n".upper())
                transfer.write(f"Status da transação: {status}\n".upper())

    # Aqui tem a mesma finalidade que a parte de cima, porem a cada 5 segundos, enquanto status do pagamento for pendente (pending), o app se mantem aberto e verificando o status
    while True:
        status = check_payment_status(payment_id)
        print(f"Status do pagamento: {status}")
        if status in ['approved', 'rejected', 'cancelled', 'in_process']:
            if status in 'approved':
                salvar_log_transfer()
                break
            break
        time.sleep(5)