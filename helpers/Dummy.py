SSH = {
    'df': f"""Filesystem           1K-blocks      Used  Available Use% Mounted on
devtmpfs              32747380         0   32747380   0% /dev
tmpfs                 32778352         0   32778352   0% /dev/shm
tmpfs                 32778352   3263304   29515048  10% /run
tmpfs                 32778352         0   32778352   0% /sys/fs/cgroup
/dev/mapper/cl-root  523749376 243071992  280677384  47% /
/dev/sda2              1028096    246900     781196  25% /boot
/dev/mapper/cl-home 1609818112 349130120 1260687992  22% /home
tmpfs                  6555668        16    6555652   1% /run/user/42
overlay              523749376 243071992  280677384  47% /var/lib/docker/overlay2/ba50fa5a8790c9c52728335c0cc80394f7e15d8dcc2379cffc8f7be549e27d18/merged
tmpfs                  6555668         0    6555668   0% /run/user/0
overlay              523749376 243071992  280677384  47% /var/lib/docker/overlay2/93a453f4f71275eda07f0d4f0725accf14fff927eaf21fc93e2b6c32b610e100/merged
overlay              523749376 243071992  280677384  47% /var/lib/docker/overlay2/96049fae47bc8b5a94a4906ae573ed218754863b7e2465a7e6b98a5154aad689/merged
overlay              523749376 243071992  280677384  47% /var/lib/docker/overlay2/7daeb9bc0bfb9ae36e54482c87a4908b726e91383d4319cad5dd812bbd04b3e9/merged
overlay              523749376 243071992  280677384  47% /var/lib/docker/overlay2/30449656b3c81c1ff5cf703353e39c0f201c1f7406a1cb8d3edbe6d2a7243a86/merged
overlay              523749376 243071992  280677384  47% /var/lib/docker/overlay2/5fdbb0c7b151db1ec413fefaead12bc366ae10d51bf4bfee300d21d02e7506b9/merged
overlay              523749376 243071992  280677384  47% /var/lib/docker/overlay2/af8f3fb9308d4f1239c1db9a702d1dada1cdc4a5fc2aff7f8894c045f9c29619/merged
overlay              523749376 243071992  280677384  47% /var/lib/docker/overlay2/c44ab0300aad3ab36429eac66a2739de94118d2b20a1f4ee8b16afa9785463af/merged
overlay              523749376 243071992  280677384  47% /var/lib/docker/overlay2/e14516bb7dab2e49a598a0d2507f7f43691d1759c2b977d92828fa529233a7df/merged
overlay              523749376 243071992  280677384  47% /var/lib/docker/overlay2/20a1115a439c73f5e40f59733409a9334fc73fcbbae5861b7dc52871d0f9c60b/merged
overlay              523749376 243071992  280677384  47% /var/lib/docker/overlay2/ff08b32ec08efcb99bdb727ae8e6ca8fef075f47ca02a3c3496770a32e34bc91/merged
overlay              523749376 243071992  280677384  47% /var/lib/docker/overlay2/e62a9e3892b9895efa20ff123ec71ae6004677598f78936d4677c38bb53cc29b/merged""",
    'df -h': f"""Filesystem           1K-blocks      Used  Available Use% Mounted on
devtmpfs              32747380         0   32747380   0% /dev
tmpfs                 32778352         0   32778352   0% /dev/shm
tmpfs                 32778352   3263304   29515048  10% /run
tmpfs                 32778352         0   32778352   0% /sys/fs/cgroup
/dev/mapper/cl-root  523749376 243071992  280677384  47% /
/dev/sda2              1028096    246900     781196  25% /boot
/dev/mapper/cl-home 1609818112 349130120 1260687992  22% /home
tmpfs                  6555668        16    6555652   1% /run/user/42
overlay              523749376 243071992  280677384  47% /var/lib/docker/overlay2/ba50fa5a8790c9c52728335c0cc80394f7e15d8dcc2379cffc8f7be549e27d18/merged
tmpfs                  6555668         0    6555668   0% /run/user/0
overlay              523749376 243071992  280677384  47% /var/lib/docker/overlay2/93a453f4f71275eda07f0d4f0725accf14fff927eaf21fc93e2b6c32b610e100/merged
overlay              523749376 243071992  280677384  47% /var/lib/docker/overlay2/96049fae47bc8b5a94a4906ae573ed218754863b7e2465a7e6b98a5154aad689/merged
overlay              523749376 243071992  280677384  47% /var/lib/docker/overlay2/7daeb9bc0bfb9ae36e54482c87a4908b726e91383d4319cad5dd812bbd04b3e9/merged
overlay              523749376 243071992  280677384  47% /var/lib/docker/overlay2/30449656b3c81c1ff5cf703353e39c0f201c1f7406a1cb8d3edbe6d2a7243a86/merged
overlay              523749376 243071992  280677384  47% /var/lib/docker/overlay2/5fdbb0c7b151db1ec413fefaead12bc366ae10d51bf4bfee300d21d02e7506b9/merged
overlay              523749376 243071992  280677384  47% /var/lib/docker/overlay2/af8f3fb9308d4f1239c1db9a702d1dada1cdc4a5fc2aff7f8894c045f9c29619/merged
overlay              523749376 243071992  280677384  47% /var/lib/docker/overlay2/c44ab0300aad3ab36429eac66a2739de94118d2b20a1f4ee8b16afa9785463af/merged
overlay              523749376 243071992  280677384  47% /var/lib/docker/overlay2/e14516bb7dab2e49a598a0d2507f7f43691d1759c2b977d92828fa529233a7df/merged
overlay              523749376 243071992  280677384  47% /var/lib/docker/overlay2/20a1115a439c73f5e40f59733409a9334fc73fcbbae5861b7dc52871d0f9c60b/merged
overlay              523749376 243071992  280677384  47% /var/lib/docker/overlay2/ff08b32ec08efcb99bdb727ae8e6ca8fef075f47ca02a3c3496770a32e34bc91/merged
overlay              523749376 243071992  280677384  47% /var/lib/docker/overlay2/e62a9e3892b9895efa20ff123ec71ae6004677598f78936d4677c38bb53cc29b/merged""",
    'free -m': f"""              total        used        free      shared  buff/cache   available
Mem:          64020       11246        5615        2900       47158       49269
Swap:         99075         335       98740""",
    'free': f"""              total        used        free      shared  buff/cache   available
Mem:       65556704    11517324     5749232     2969720    48290148    50450696
Swap:     101453820      343040   101110780"""
}