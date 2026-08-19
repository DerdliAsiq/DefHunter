#!/usr/bin/env python3
import argparse
import socket
import ftplib
import subprocess
import concurrent.futures
import sys
import time

try:
    import paramiko
    import requests
    import pymysql
    from ldap3 import Server, Connection, ALL
    import logging
    logging.getLogger("paramiko").setLevel(logging.CRITICAL)
    requests.packages.urllib3.disable_warnings()
except ImportError as e:
    print(f"\033[91m[!] Kütüphane eksiği var: {e}\033[0m")
    sys.exit(1)

def print_banner():
    banner = """
\033[1;31m    ____       \033[1;36m________  __            __           \033[0m
\033[1;31m   / __ \___  \033[1;36m/ __/ / / / /_  ______  / /____  _____\033[0m
\033[1;31m  / / / / _ \\\033[1;36m/ /_  / /_/ / / / / __ \/ __/ _ \/ ___/\033[0m
\033[1;31m / /_/ /  __/\033[1;36m __/ / __  / /_/ / / / / /_/  __/ /    \033[0m
\033[1;31m/_____/\___/\033[1;36m_/   /_/ /_/\__,_/_/ /_/\__/\___/_/     \033[0m
\033[1;90m==============================================================\033[0m
\033[1;92m [+] DEFHUNTER v2.1 - OMNI-SCAN VULNERABILITY ENGINE\033[0m
\033[1;92m [+] AUTHOR: DERDLIASIQ | TARGET PERSONA: TassakliSabri\033[0m
\033[1;90m==============================================================\033[0m
"""
    print(banner)

def check_port(ip, port, timeout=2):
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(timeout)
            return s.connect_ex((ip, port)) == 0
    except: return False

def check_ftp_anonymous(ip):
    print(f"\033[94m[*] [FTP] Anonymous deneniyor...\033[0m")
    try:
        ftp = ftplib.FTP()
        ftp.connect(ip, 21, timeout=5)
        ftp.login('anonymous', 'anonymous@example.com')
        print(f"\033[1;92m[+] [FTP] {ip}:21 -> Anonymous login BAŞARILI!\033[0m")
        ftp.quit()
    except: print(f"\033[91m[-] [FTP] Kapalı.\033[0m")

def check_ssh_defaults(ip):
    print(f"\033[94m[*] [SSH] Default parolalar deneniyor...\033[0m")
    creds = [('sabri', '123456'), ('root', 'root'), ('admin', 'admin'), ('msfadmin', 'msfadmin')]
    for user, pwd in creds:
        try:
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect(ip, port=22, username=user, password=pwd, timeout=4)
            print(f"\033[1;92m[+] [SSH] {ip}:22 -> BİNGO! ({user}:{pwd})\033[0m")
            ssh.close()
            return
        except: continue
    print(f"\033[91m[-] [SSH] Parolalar başarısız.\033[0m")

def check_smb_null(ip):
    print(f"\033[94m[*] [SMB] Null Session deneniyor...\033[0m")
    try:
        # \\ yerine // kullanmak Linux smbclient için daha stabil
        cmd = ['smbclient', '-L', f'//{ip}', '-N']
        result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, timeout=10)
        output = result.stdout
        
        if "Sharename" in output or "Disk" in output or "Anonymous login successful" in output:
            print(f"\033[1;92m[+] [SMB] {ip}:445 -> Null Session BAŞARILI! Paylaşımlar açık.\033[0m")
            if "TassakliSabrininSirlari" in output:
                print(f"\033[1;95m    >>> DİKKAT: 'TassakliSabrininSirlari' TESPİT EDİLDİ! <<<\033[0m")
        else:
            print(f"\033[91m[-] [SMB] Erişim reddedildi.\033[0m")
    except Exception as e:
        print(f"\033[91m[-] [SMB] Hata: {e}\033[0m")

def check_redis_unauth(ip):
    print(f"\033[94m[*] [REDIS] Unauth deneniyor...\033[0m")
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(3)
        s.connect((ip, 6379))
        s.sendall(b"*1\r\n$4\r\nPING\r\n")
        resp = s.recv(1024)
        if b"+PONG" in resp:
            print(f"\033[1;92m[+] [REDIS] {ip}:6379 -> Unauthenticated erişim AÇIK!\033[0m")
        s.close()
    except: print(f"\033[91m[-] [REDIS] Kapalı.\033[0m")

def check_mysql_blank(ip):
    print(f"\033[94m[*] [MYSQL] Blank root password deneniyor...\033[0m")
    try:
        conn = pymysql.connect(host=ip, user='root', password='', connect_timeout=3)
        print(f"\033[1;92m[+] [MYSQL] {ip}:3306 -> 'root' PAROLASIZ!\033[0m")
        conn.close()
    except: print(f"\033[91m[-] [MYSQL] Korumalı.\033[0m")

def check_ldap_anon(ip):
    print(f"\033[94m[*] [LDAP] Anon bind deneniyor...\033[0m")
    try:
        server = Server(ip, get_info=ALL)
        conn = Connection(server, auto_bind=True, receive_timeout=3)
        print(f"\033[1;92m[+] [LDAP] {ip}:389 -> Anonymous Bind BAŞARILI!\033[0m")
        conn.unbind()
    except: print(f"\033[91m[-] [LDAP] Kapalı.\033[0m")

def check_rsync_anon(ip):
    print(f"\033[94m[*] [RSYNC] Anon deneniyor...\033[0m")
    try:
        cmd = ['rsync', f'rsync://{ip}']
        res = subprocess.run(cmd, capture_output=True, text=True, timeout=5)
        if res.stdout:
            print(f"\033[1;92m[+] [RSYNC] {ip}:873 -> Açık modüller var!\033[0m")
        else: print(f"\033[91m[-] [RSYNC] Kapalı.\033[0m")
    except: print(f"\033[91m[-] [RSYNC] Hata.\033[0m")

def check_web_dir_listing(ip, port):
    print(f"\033[94m[*] [WEB] Directory Listing deneniyor ({port})...\033[0m")
    try:
        r = requests.get(f"http://{ip}:{port}/", timeout=3, verify=False)
        if "Index of /" in r.text or "Directory Listing For" in r.text:
            print(f"\033[1;92m[+] [WEB] {ip}:{port} -> Directory Listing AÇIK!\033[0m")
        else: print(f"\033[91m[-] [WEB] Korumalı ({port}).\033[0m")
    except: print(f"\033[91m[-] [WEB] Bağlantı reddedildi ({port}).\033[0m")

def check_tomcat_manager(ip):
    print(f"\033[94m[*] [TOMCAT] Manager default creds deneniyor...\033[0m")
    creds = [('tomcat','tomcat'), ('admin','admin'), ('tomcat','s3cret'), ('sabri','123456')]
    for u, p in creds:
        try:
            r = requests.get(f"http://{ip}:8080/manager/html", auth=(u,p), timeout=3, verify=False)
            if r.status_code == 200:
                print(f"\033[1;92m[+] [TOMCAT] {ip}:8080 -> Panel kırıldı! ({u}:{p})\033[0m")
                return
        except: continue
    print(f"\033[91m[-] [TOMCAT] Korumalı.\033[0m")

def main():
    print_banner()
    parser = argparse.ArgumentParser()
    parser.add_argument("-t", "--target", required=True)
    args = parser.parse_args()
    target_ip = args.target

    print(f"\033[1;93m[*] {target_ip} için Omni-Scan başlatılıyor...\033[0m")
    
    ports_to_check = {
        21: "FTP", 22: "SSH", 80: "HTTP", 139: "SMB", 389: "LDAP", 
        445: "SMB", 873: "RSYNC", 3306: "MYSQL", 6379: "REDIS", 8080: "HTTP-ALT"
    }
    
    open_ports = []
    for port, name in ports_to_check.items():
        if check_port(target_ip, port):
            open_ports.append(port)
            print(f"\033[94m[+] Port {port} ({name}) AÇIK\033[0m")

    if not open_ports:
        print("\033[91m[!] Kritik portlardan hiçbiri açık değil.\033[0m")
        sys.exit(0)

    print("\033[1;93m[*] Modüller ateşleniyor...\033[0m\n")

    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        if 21 in open_ports: executor.submit(check_ftp_anonymous, target_ip)
        if 22 in open_ports: executor.submit(check_ssh_defaults, target_ip)
        if 80 in open_ports: executor.submit(check_web_dir_listing, target_ip, 80)
        if 139 in open_ports or 445 in open_ports: executor.submit(check_smb_null, target_ip)
        if 389 in open_ports: executor.submit(check_ldap_anon, target_ip)
        if 873 in open_ports: executor.submit(check_rsync_anon, target_ip)
        if 3306 in open_ports: executor.submit(check_mysql_blank, target_ip)
        if 6379 in open_ports: executor.submit(check_redis_unauth, target_ip)
        if 8080 in open_ports: 
            executor.submit(check_web_dir_listing, target_ip, 8080)
            executor.submit(check_tomcat_manager, target_ip)

    print("\n\033[1;90m" + "=" * 62 + "\033[0m")
    print("\033[1;92m[+] Omni-Scan Operasyonu Tamamlandı.\033[0m")

if __name__ == "__main__":
    main()