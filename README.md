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

