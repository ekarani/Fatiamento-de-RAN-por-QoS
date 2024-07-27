# Fatiamento de RAN por QoS
_Testes feitos numa VM Ubuntu 22.04_

## Preparando ambiente
* Pré-requisito: [Ansible](https://docs.ansible.com/ansible/latest/installation_guide/intro_installation.html#installing-and-upgrading-ansible-with-pip)

### Arquivos que devem ser alterados:
* `ansible.cfg`
```
[defaults]
inventory = ./ansible/inventory 
remote_user = ubuntu	# Change Here 
ask_pass = false

[privilege_escalation]
become = true
become_method = sudo
become_user = root
become_ask_pass = false
```
* `./ansible/inventory/hosts`

Atualizar os IPs dos hosts e caminho das chaves ssh. (Recomendável que gNB e CORE estejam no mesmo host).

```
[core]
1.1.1.1 ansible_ssh_private_key_file=[ssh_key_path]

[gnb]
2.2.2.2 ansible_ssh_private_key_file=[ssh_key_path]

[ue]
3.3.3.3 ansible_ssh_private_key_file=[ssh_key_path]

[ran:children]
gnb
ue
```

* **Instalação de Pacotes**

```
ansible-playbook ansible/playbooks/install-ubuntu-packages.yaml
```

* **Instalando Docker, Baixando Imagens e Executando CORE**

```
ansible-playbook ansible/playbooks/set-docker.yaml
```

* **Baixando e Compilando Repositório OAI RAN**

```
ansible-playbook ansible/playbooks/build-ran.yaml
```

* **Baixando e Compilando Repositório OAI FlexRIC**

```
ansible-playbook ansible/playbooks/build-flexric.yaml
```

## Executando
1. Executando FlexRIC
```
cd flexric/build/examples/ric/
./nearRT-RIC
```

2. Executando gNB
```
cd oai/cmake_targets/ran_build/build/
sudo ./nr-softmodem --rfsim --sa -O ./gnb.conf --continuous-tx --gNBs.[0].min_rxtxtime 6
```

3. Executando UE
```
cd oai/cmake_targets/ran_build/build/
sudo ./nr-uesoftmodem -r 106 --numerology 1 --band 78 -C 3619200000 --rfsim --sa --nokrnmod --rfsimulator.serveraddr 127.0.0.1 -O ue.conf
```

# Descrição do Experimento que originou o diretório "dados"
1. Geração de carga para o UE 2 sem executar script de monitoramento e fatiamento
2. Geração de carga para os dois UEs ao mesmo tempo sem o script de monitoramento e fatiamento
3. Execução do script python `slicing.py`, que realiza monitoramento com o xApp `xapp_kpm_moni` em loop e gatilha o fatiamento quando a UE 1 apresenta latência de downlink maior que 0.5 ms

Os estresses na rede com iperf3 são feitos da seguinte forma:
1. Executar iperf com `-t 60` para UE 1, sendo somente ele por 10 segundos
2. Executar iperf com `-t 60` para UE 2
O comportamento da taxa de transferência é observado durante esse tempo.

Ainda é realizado iperf com cada UE sozinho após o fatiamento.


