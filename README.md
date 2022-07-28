# Monitoramento

Ferramenta de monitoramento para os projetos do laboratório BioBD da PUC-Rio

Esse projeto integra a ferramenta de monitoramento com um banco de dados
relacionado a tempo (Prometheus) com um serviço de visualização (Grafana)

A ferramenta também envia os status atuais dos módulos testados para 
[statuspage](https://statuspage.io), assim como também envia notificações
para um servidor [Discord](https://discord.com)

## Requerimentos

A ferramenta utiliza [Docker](https://docker.com) para criar os containers.

Caso prefira não utilizar Docker, será necessário a instalação de [Python](https://python.org)
e de [Redis](https://redis.io) para a ferramenta, assim como os serviços do [Prometheus](https://prometheus.io) e 
do [Grafana](https://grafana.com) para o funcionamento completo do serviço de monitoramento

Caso queira enviar os status para a statuspage, ou notificar por Discord,
será necessário as credenciais de acesso para a API dos respectivos serviços

## Instalação

Primeiro, crie o arquivo `app/config.toml`. Um modelo do arquivo está 
disponível em `app/example.config.toml`.

O arquivo de configuração possui o seguinte formato:

```toml
version = 1.0       # versao da ferramenta
interval = 100      # intervalo da execução da ferramenta em segundos
port = 2112         # porta para disponiblizar os resultados

[statuspage]        # configurações relativas a statuspage
apikey = "xxx"      # api key da statuspage
pageid = "xxx"      # id da página da statuspage

[discord]
role_id = "xxx"     # identificador da role que será sempre marcada por qualquer notificação
id = "xxx"          # identificador do bot
token = "xxx"       # token do bot

[redis]
host = 'xxx'        # ip do redis. Caso esteja usando docker-compose, deixar 'redis'
port = 6379         # porta do redis

# cada [[modules]] representa um módulo de teste
[[modules]]
name = 'meu_modulo_de_teste'    # nome do modulo
statuspage_id = 'xxx'           # id do componente a ser atualizado na statuspage
notify = ['xxx', 'yyy']         # lista dos identificadores das roles a serem marcadas no discord
[[modules.test]]                # o tipo de teste a ser feito
type = "http | port | size"     # algum dos tres tipos possiveis
url = 'xxx'                     # APENAS NO MODO HTTP OU SIZE
method = 'get | post'           # APENAS NO MODO HTTP OU SIZE
host = 'xxx'                    # APENAS NO MODO PORT
port = 1234                     # APENAS NO MODO PORT

# outros módulos...
```

Feito o arquivo de configuração, execute todos os serviços atraves do `docker-compose`:

```bash
docker-compose up --build
```

Caso queira executar somente a ferramenta de monitoramento:

```bash
cd app
docker build --tag monitoramento .
docker run --name monitor monitoramento
```

Caso queira executar sem utilizar docker, será necessário ter uma instância Redis rodando, e ter o python
instalado (substitua `python` por `python3` em sistemas linux/mac). É recomendado o uso de um 
[ambiente virtual](https://packaging.python.org/en/latest/guides/installing-using-pip-and-virtual-environments/#creating-a-virtual-environment)

```bash
cd app
python -m pip install -r requirements.txt
python main.py
```

## Funcionamento dos testadores

Há três casos de uso para os testadores

### HTTP

Um testador do tipo HTTP vai consultar uma página web e esperar a sua resposta. Caso a resposta seja um código 200, 
o testador considera que o módulo está *OPERACIONAL*. 
Caso seja um código 5xx, o módulo está em *UNDER MAINTANCE*
Caso contrário, o módulo está em *MAJOR OUTAGE*

### PORT

Um testador do tipo PORT vai tentar abrir um socket com um servidor por uma porta. Caso a conexão seja efetuada
com sucesso, o testador considera que o módulo está *OPERACIONAL*. Caso contrário, o módulo está em *MAJOR OUTAGE*

### SIZE

Um testador do tipo SIZE vai consultar uma página web que retorna um json no seguinte formato:

```json
{"porcentagem": 0.123}
```

Onde porcentagem é um número entre 0 e 1, que representa a fração de uso atual do projeto.

* Caso a porcentagem seja menor que 50%, é considerado um estado de *OPERACIONAL*
* Caso a porcentagem esteja entre 50% e 70%, é considerado um estado de *DEGRADED_PERFORMANCE*
* Caso a porcentagem esteja entre 70% e 90%, é considerado um estado de *PARTIAL_OUTAGE*
* Caso a porcentagem seja maior que 90%, é considerado um estado de *MAJOR_OUTAGE*
