import subprocess

def get_dsa_signature(filename, private_key):
    '''get the dsa signature for a file using the supplied private key'''

    process1 = subprocess.Popen(['openssl', 'dgst', '-sha1', '-binary', filename],
                                stdout=subprocess.PIPE)

    if process1.wait() != 0:
        return None

    process2 = subprocess.Popen(['openssl', 'dgst', '-dss1', '-sign',
                                 private_key], stdin=process1.stdout, stdout=subprocess.PIPE)

    if process2.wait() != 0:
        return None

    process3 = subprocess.Popen(['openssl', 'enc', '-base64'],
                                stdin=process2.stdout, stdout=subprocess.PIPE)

    process1.stdout.close()
    process2.stdout.close()

    output = process3.communicate()[0].strip()

    if process3.returncode != 0:
        return None

    return output
