from hashlib import sha1

def file_sha1(file_path):
    sha1_hash = sha1()
    with open(file_path, 'rb') as f:
        while True:
            data = f.read(4096)
            if not data:
                break
            sha1_hash.update(data)
    return sha1_hash.hexdigest()
