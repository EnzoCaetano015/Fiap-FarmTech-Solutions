"""Preflight somente leitura por padrão; criação explícita do tópico e assinatura."""
import argparse
import ipaddress
import json


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=["preflight", "sns", "security-group"])
    parser.add_argument("--region", default="us-east-1")
    parser.add_argument("--email")
    parser.add_argument("--vpc-id")
    parser.add_argument("--presenter-cidr")
    args = parser.parse_args()
    import boto3
    from botocore.config import Config
    session = boto3.Session(region_name=args.region)
    config = Config(connect_timeout=5, read_timeout=10, retries={"max_attempts": 1})
    if args.command == "preflight":
        findings = []
        checks = [("sts", "get_caller_identity", {}), ("ec2", "describe_regions", {}),
                  ("ec2", "describe_instances", {"MaxResults": 5}),
                  ("ec2", "describe_instance_type_offerings", {"Filters": [{"Name": "instance-type", "Values": ["t3.medium"]}]}),
                  ("sns", "list_topics", {})]
        for service, method, params in checks:
            try:
                response = getattr(session.client(service, config=config), method)(**params)
                details = None
                if method == "describe_instance_type_offerings":
                    details = response.get("InstanceTypeOfferings", [])
                findings.append({"service": service, "check": method, "ok": True, "details": details})
            except Exception as exc:
                code = getattr(exc, "response", {}).get("Error", {}).get("Code", type(exc).__name__)
                findings.append({"service": service, "check": method, "ok": False, "error": code})
        print(json.dumps({"region": args.region, "checks": findings,
                          "nota": "Leitura bem-sucedida não garante autorização para criar recursos; consultar instruções do laboratório."}, indent=2))
    elif args.command == "sns":
        if not args.email or "@" not in args.email:
            parser.error("Informe --email do destinatário autorizado")
        client = session.client("sns", config=config)
        topic = client.create_topic(Name="farmtech-alertas", Tags=[{"Key": "Project", "Value": "FarmTech-Fase7"}])["TopicArn"]
        subscriptions = client.get_paginator("list_subscriptions_by_topic").paginate(TopicArn=topic)
        exists = any(s.get("Endpoint") == args.email and s.get("Protocol") == "email"
                     for page in subscriptions for s in page["Subscriptions"])
        if not exists:
            client.subscribe(TopicArn=topic, Protocol="email", Endpoint=args.email)
        print(json.dumps({"FARMTECH_SNS_TOPIC_ARN": topic,
                          "proximo_passo": "Confirmar assinatura na caixa do destinatário; depois comprovar e-mail recebido."}, indent=2))
    else:
        if not args.vpc_id or not args.presenter_cidr:
            parser.error("Informe --vpc-id e --presenter-cidr IPV4/32")
        network = ipaddress.ip_network(args.presenter_cidr, strict=True)
        if network.version != 4 or network.prefixlen != 32:
            parser.error("O acesso deve ser restrito ao IPv4 do apresentador, com /32")
        ec2 = session.client("ec2", config=config)
        found = ec2.describe_security_groups(Filters=[{"Name": "group-name", "Values": ["farmtech-fase7"]},
                                                      {"Name": "vpc-id", "Values": [args.vpc_id]}])["SecurityGroups"]
        if found:
            parser.error("Grupo já existe: inspecione regras antes de alterar, sem ampliar acesso automaticamente")
        group = ec2.create_security_group(GroupName="farmtech-fase7", Description="FarmTech presenter access only", VpcId=args.vpc_id)["GroupId"]
        ec2.authorize_security_group_ingress(GroupId=group, IpPermissions=[{
            "IpProtocol": "tcp", "FromPort": port, "ToPort": port,
            "IpRanges": [{"CidrIp": str(network), "Description": "Presenter only"}]} for port in (22, 8501)])
        print(json.dumps({"SecurityGroupId": group}, indent=2))


if __name__ == "__main__":
    main()
