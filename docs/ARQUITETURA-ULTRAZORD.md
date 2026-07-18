# Arquitetura ULTRAZORD (pointer)

> **Documento canônico**: [Gabinete-do-Amom/firewall-config → docs/ARQUITETURA-ULTRAZORD.md](https://github.com/Gabinete-do-Amom/firewall-config/blob/main/docs/ARQUITETURA-ULTRAZORD.md) — decidida pelo Amom em 2026-07-11.

A fleet GDA consolida em 2× HPE DL380 Gen9 formando o cluster **ultrazord**:

- `megazord` — nó 1, produção primária (**EM PRODUÇÃO desde 2026-07-11**; substituiu o edge-gateway laptop)
- `dragonzord` — nó 2, mirror/failover/blue-green (aguardando chegada; tratar como down; IP reservado `192.168.2.19`, VIP do cluster `192.168.2.20`)
- `zordon` — witness/quorum: **serviço** no superdevops (device não muda de nome)
- `alpha5` — automação (Claude Code, scripts, Ansible, GitOps)

Regras-chave: serviço **nunca** aponta pra nó físico (sempre VIP/proxy/LB); carga crítica ≤ capacidade de 1 nó; execução Ubuntu+Docker direto no host (DECISÃO 2026-07-18: **sem Proxmox**; failover TBD); rede alvo RB5009 → CRS510-8XS-2XQ-IN (core) → CRS328 (câmeras) / CRS418 (APs). Fleet antiga (devops/n8n/jagenda/edge/HA servers) sai e vai pra **trituração** com sanitização de discos + rotação de credenciais — superdevops fica.

**Este repo**: Serviço/projeto da fleet GDA — consolida no cluster ultrazord conforme a migração avançar.