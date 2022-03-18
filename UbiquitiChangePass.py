import paramiko
from mac_vendor_lookup import MacLookup
import jarvisdb
from pythonping import ping
from allPasswords import UserDevicePass
import socket
from datetime import datetime

starttime = datetime.now()
devices = jarvisdb.Query("""
                            SELECT a.mac,
                                   a.ip
                            FROM jarvisdb.ns_accounts a
                            WHERE a.technologyID = 0
                              AND LENGTH(a.mac) = 17
                              AND a.mac NOT LIKE 'ja:rv:is:%'
                              AND a.mac LIKE '%:%'
                              AND a.ip LIKE '10.221.63.218%'
                            ORDER BY a.ip ASC
                        """)

allpasswords = UserDevicePass.allpasswordsubnt

print(len(devices))
numirate = 0


for mac, ip in devices:
    print("--------------------------------------------------------------")
    numirate += 1
    print(f"{numirate}) {ip} - {mac}")
    try:
        manufacturer = MacLookup().lookup(mac)
    except:
        print(f"{ip}  {mac} manufacturer is not identified")
        continue
    if manufacturer in ['Ubiquiti Networks Inc.', 'Routerboard.com']:
        p = ping(ip, count=1)
        if str(p)[0:5] == 'Reply':
            try:
                a_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                location = (ip, 22)
                result_of_check = a_socket.connect_ex(location)
                if result_of_check == 0:
                    port = 'open'
                    a_socket.close()
                else:
                    port = 'not open'
                    with open(r"C:\Users\giorgi\Desktop\SSH Port is Not Open.txt", "a") as file_object:
                        file_object.write(f"{ip}\n")
                    print(f"{ip} --- SSH Port Is Not Open.")
                    print("--------------------------------------------------------------")
                    a_socket.close()
                    continue
            except:
                print("Port Is Not open")
        else:
            p = 'None'
            port = 'not open'
            print("Ping not suceffuly")
            continue
        if str(p)[0:5] == 'Reply' and port == 'open':
            print(f"{ip} - Password Guessing Started...")
            try:
                for i in allpasswords:
                    client = paramiko.SSHClient()
                    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                    try:
                        connect = client.connect(ip, username=i[0], password=i[1])
                    except:
                        print(f"Conttiniu {i}")
                        client.close()
                        continue

                    if [connect][0] == None and i[1] == 'ubnt1' or i[1] == 'q1w2Admin' or i[1] == 'q1w2Admin' or i[1] == 'admin1':
                        print(f"Password Already Changed - {ip}")
                        print("--------------------------------------------------------------")
                        break
                    else:
                        try:
                            stdin, stdout, stderr = client.exec_command(
                                "sed -e 's#users\.1\.name=.*#users.1.name=ubnt#' -i /tmp/system.cfg && sed -e 's#users\.1\.password=.*#users.1.password=$1$BjFV4v11$jWx7ktyTIZKemHRJrukFw/#' -i /tmp/system.cfg && cfgmtd -w -f /tmp/system.cfg && reboot")
                            print("Username and Password Changed Successfully")
                            for line in stdout:
                                print(line.strip('\n'))
                                if [line][0][0:12] == 'syntax error':
                                    stdin, stdout, stderr = client.exec_command("/user add name=admin group=full password=admin1")
                                    stdin, stdout, stderr = client.exec_command("/user set [find name=admin] password=admin1")
                                    print("Mikrotik Add New Password")
                                print("Username and Password Changed Successfully")
                                stdin.close()
                                client.close()
                                break
                        except OSError or paramiko.SSHException or paramiko.transport or TimeoutError or paramiko.ssh_exception.SSHException or paramiko.ssh_exception.NoValidConnectionsError:
                            print("SSHException, OSError ")
                            break
                        except:
                            print("SSHException, OSError ")
                            break

                        print("--------------------------------------------------------------")
                        break
            except:
                print("Errrrooooorrrr")
            if len(allpasswords) == allpasswords.index(i) + 1:
                with open(r"C:\Users\giorgi\Desktop\Wrong Username or Password.txt", "a") as file_object:
                    file_object.write(f"{ip}\n")
                    print("Password is Not Changed")
                continue

        else:
            with open(r"C:\Users\giorgi\Desktop\Ping - Request timed out.txt", "a") as file_object:
                file_object.write(f"{ip}\n")
    else:
        print(f"{ip}  {manufacturer}Other manufacturer")
        print("--------------------------------------------------------------")



print(datetime.now() - starttime)
print(ip, mac)
