apt-get update
apt-get install vim

# vscode config
# Host runpod
#     HostName 194.26.196.6
#     User root
#     Port 43459
#     IdentityFile C:\Users\Leszek\.ssh\id_ed25519





# ssh_boot.sh
ssh_key_ops () {
    ak="/root/.ssh/authorized_keys2"

    if [ -f "$ak" ]; then
        rm "$ak"
    fi

    touch "/root/.ssh/authorized_keys2"
    # dom
    echo -e "ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIBLNp5MWZMY664OoV6q0e/wjrUscflSfKDubqwiSGgkC rhoninn.11@gmail.com\n" >> "/root/.ssh/authorized_keys2"
    # laptop
    echo -e "ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAICqIjh1ubUXYL3csoo16QxYHzJtQTOG9pF/r/g/vsT49 adamGrzelak@wp.pl\n" >> "/root/.ssh/authorized_keys2"
    # laptop
    echo -e "ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAINxgsRCA8bRjzqUcwoaHmuasGfEouyaO7oijTY49ukGp adamGrzelak@wp.pl\n" >> "/root/.ssh/authorized_keys2"
    cat "/root/.ssh/authorized_keys2"
}


ssh_key_ops


# sd_boot
node_install() {

    apt-get update
    apt-get install -y ca-certificates curl gnupg
    mkdir -p /etc/apt/keyrings
    curl -fsSL https://deb.nodesource.com/gpgkey/nodesource-repo.gpg.key | gpg --dearmor -o /etc/apt/keyrings/nodesource.gpg

    NODE_MAJOR=18
    echo "deb [signed-by=/etc/apt/keyrings/nodesource.gpg] https://deb.nodesource.com/node_$NODE_MAJOR.x nodistro main" | tee /etc/apt/sources.list.d/nodesource.list

    # apt-get remove libnode-dev
    apt-get update
    apt-get install nodejs -y

}

web_sd_install () {
    my_wd="/root/tmp"
    web_Sd="https://github.com/rhoninn11/web_sd.git"
    web_Sd_back="https://github.com/rhoninn11/web_sd_back.git"
    web_Sd_front="https://github.com/rhoninn11/web_sd_front.git"

    cd $my_wd
    git clone $web_Sd
    git clone $web_Sd_back
    git clone $web_Sd_front
    
    web_sd_wd="$my_wd/web_sd"
    web_sd_back_wd="$my_wd/web_sd_back"
    web_sd_front_wd="$my_wd/web_sd_front"

    cd $web_sd_wd
    pip install -r ./req.txt

    cd $web_sd_back_wd
    npm install
    mkdir "$web_sd_back_wd/tmp"
    cd $web_sd_front_wd
    npm install
}

create_key_and_cert () {
    openssl genpkey -algorithm RSA -out private-key.pem -pkeyopt rsa_keygen_bits:2048
    openssl req -new -x509 -key private-key.pem -out certificate.pem -days 365
}


node_install
web_sd_install
# vs_ccode

# run.sc.sh

my_py_conf() {
    alias python=python3
    export PYTHONPATH="$PYTHONPATH:$(pwd)/src"
}

run_central () {
    my_wd="/root/tmp"
    web_sd_wd="$my_wd/web_sd"
    cd $web_sd_wd
    my_py_conf
    python ./src/serv/central/main.py
}

run_edge () {
    if [ "$#" -ne 1 ]; then
        echo "cuda dev not specified"
        return 1
    fi

    my_wd="/root/tmp"
    web_sd_wd="$my_wd/web_sd"
    cd $web_sd_wd
    my_py_conf

    numval=$1
    port=$((6203 + numval))
    cuda_device="cuda:$numval"

    python ./src/serv/edge/main.py $port $cuda_device

}

run_back () {
    my_wd="/root/tmp"
    web_sd_back_wd="$my_wd/web_sd_back"
    cd $web_sd_back_wd
    npm run serve
}

build_front () {
    my_wd="/root/tmp"
    web_sd_back_wd="$my_wd/web_sd_back"
    web_sd_front_wd="$my_wd/web_sd_front"
    cd $web_sd_front_wd
    my_py_conf
    npm run build
    cp -r "$web_sd_front_wd/dist" "$web_sd_back_wd/public"
}
