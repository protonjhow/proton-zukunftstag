#!/bin/sh
# Starts a dev-mode Vault and creates the transit key the chat "VPN" uses.
# Dev mode keeps everything in memory, so this runs on every container start.
set -e

vault server -dev &
VAULT_PID=$!

until vault status >/dev/null 2>&1; do sleep 0.5; done

vault secrets list | grep -q '^transit-nats/' || vault secrets enable -path=transit-nats transit
vault read transit-nats/keys/demo_key >/dev/null 2>&1 || vault write -f transit-nats/keys/demo_key
echo "transit-nats/demo_key ready"

wait "$VAULT_PID"
