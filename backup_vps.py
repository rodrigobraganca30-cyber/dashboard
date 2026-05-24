import json
import paramiko
import os
import time

def backup_vps():
    config_path = r"C:\Users\SVOBODA\Desktop\DASHBOARD\config_servidor.json"
    with open(config_path, "r") as f:
        config = json.load(f)
        
    host = config["HOST"]
    port = config["PORT"]
    user = config["USER"]
    password = config["PASS"]
    remote_dir = config["REMOTE_DIR"]
    
    print(f"Conectando a {host}...")
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        client.connect(host, port=port, username=user, password=password)
        print("Conectado com sucesso!")
        
        # O diretório no config é /docker/dashboard/html
        parent_dir = os.path.dirname(remote_dir)
        base_name = os.path.basename(remote_dir)
        
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        remote_tar = f"/tmp/dashboard_backup_{timestamp}.tar.gz"
        local_tar = rf"C:\Users\SVOBODA\Desktop\VPS_DASHBOARD_backup_{timestamp}.tar.gz"
        
        print(f"Compactando {remote_dir} no servidor para {remote_tar}...")
        cmd = f"tar -czf {remote_tar} -C {parent_dir} {base_name}"
        stdin, stdout, stderr = client.exec_command(cmd)
        exit_status = stdout.channel.recv_exit_status()
        
        if exit_status == 0:
            print("Compactação concluída. Baixando arquivo...")
            sftp = client.open_sftp()
            sftp.get(remote_tar, local_tar)
            sftp.close()
            print(f"Download concluído! Salvo em: {local_tar}")
            
            # Limpa o arquivo no servidor
            client.exec_command(f"rm {remote_tar}")
        else:
            print(f"Erro ao compactar: {stderr.read().decode('utf-8')}")
            
    except Exception as e:
        print(f"Erro na conexão: {e}")
    finally:
        client.close()

if __name__ == '__main__':
    backup_vps()
