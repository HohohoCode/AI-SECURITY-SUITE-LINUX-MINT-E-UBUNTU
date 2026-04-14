#!/bin/bash
# Script para executar o programa sem terminal visível

# Esconde o terminal e executa o programa
nohup sudo python3 ~/Downloads/AI-SECURITY-SUITE-LINUX-MINT-E-UBUNTU-main/run.py > /dev/null 2>&1 &

echo "✅ AI Security Suite iniciado em segundo plano!"
echo "Para ver a janela, verifique o ícone na bandeja do sistema"
