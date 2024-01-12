Commands for the geth chain.

```shell
# node2
geth --datadir node2 --port 30306 --bootnodes enode://b6b691afaeeafadad6cd668824fde8ce7b9717a3b98b7eaf7c517c12dab4e194a6b06c337f51f712c091a71d46cf1e969ed9bdc9cbe13b2a5679fdf404a8fd31@10.8.1.45:0?discport=30305  --networkid 12345678 --unlock 0x4CB4217A362A1456001442eD3389f2297eFce54e --password node2/password.txt --authrpc.port 8551  --rpc.enabledeprecatedpersonal --allow-insecure-unlock --vmdebug --http --http.api 'web3,eth,net,debug,personal' --http.corsdomain '*' --syncmode full --http.port 8547 --metrics --metrics.expensive --metrics.influxdb --metrics.influxdb.database "bfl" --metrics.influxdb.endpoint "http://0.0.0.0:8086" --metrics.influxdb.username "bfl" --metrics.influxdb.password "bfl123" --http.addr "10.8.1.45" --rpc.gascap 0 --mine --miner.etherbase=0x4CB4217A362A1456001442eD3389f2297eFce54e
```
