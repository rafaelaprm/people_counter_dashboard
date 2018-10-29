## Configuracoes de banco

    sudo apt-get update
    sudo apt-get install postgresql postgresql-contrib

# configurar o pg_hba.conf
    cd /etc/postgresql/10/main 
    sudo gedit pg_hba.conf
# nas ultimas linhas, troque pelas seguintes linhas

    # DO NOT DISABLE!
    # If you change this first entry you will need to make sure that the
    # database superuser can access the database using some other method.
    # Noninteractive access to all databases is required during automatic
    # maintenance (custom daily cronjobs, replication, and similar tasks).
    #
    # Database administrative login by Unix domain socket
    local   all             postgres                                trust

    # TYPE  DATABASE        USER            ADDRESS                 METHOD

    # "local" is for Unix domain socket connections only
    local   all             all                                     trust
    # IPv4 local connections:
    host    all             all             127.0.0.1/32            trust
    # IPv6 local connections:
    host    all             all             ::1/128                 trust
    # Allow replication connections from localhost, by a user with the
    # replication privilege.
    local   replication     all                                     trust
    host    replication     all             127.0.0.1/32            trust
    host    replication     all             ::1/128                 trust


# criar o banco local 
    sudo service postgresql restart
    sudo -u postgres psql       # abre o prompt do postgres 
    CREATE DATABASE peoplecounter;



## Criar ambiente virtual (dentro da pasta do projeto peoplecounter)
    pip install virtualenv
    virtualenv -p python3 venv



## Ativar ambiente virtual
    source venv/bin/activate


## Instalar dependencias
    pip3 install -r requirements.txt


## Criar banco local (rodar esse somente uma vez)
    python3 models.py


## Rodar contador de pessoas 
    python3 start.py


## Para ver o conteudo do banco 
    sudo -u postgres psql
    \c peoplecounter;
# exemplo de select
    select c.camera_id, c.nome as camera, l.nome as local, l.endereco, cl.nome as cliente 
    from cameras c 
    left join locais l on c.local_id = l.local_id 
    left join clientes cl ON l.cliente_id = cl.cliente_id; 


