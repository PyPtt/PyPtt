import os

# 取得目前腳本的路徑
_script_path = os.path.dirname(os.path.abspath(__file__))


def generate_ssl_certificate():
    # 呼叫 shell 腳本來生成 SSL 憑證
    os.system(f'sh {_script_path}/gen_ssl.sh')

    print('SSL certificate generated successfully.')

    # 讀取生成的憑證
    with open('./key.pem', 'r') as key_file, open('./cert.pem', 'r') as cert_file:
        key = key_file.read()
        cert = cert_file.read()

    # 將憑證內容轉換成字串格式
    key = f'key = """{key}"""'
    cert = f'cert = """{cert}"""'

    # 組合 SSL 上下文設定字串
    ssl_context = f"{key}\n\n{cert}"

    # 將 SSL 上下文設定寫入文件
    with open(f'{_script_path}/../PyPtt/ssl_config.py', 'w') as f:
        f.write(ssl_context)

    # 刪除生成的憑證檔案
    os.remove('./key.pem')
    os.remove('./cert.pem')
    os.remove('./csr.pem')


if __name__ == '__main__':
    generate_ssl_certificate()
