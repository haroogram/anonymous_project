# Packer 변수 설정 예시 파일
# 이 파일을 variables.pkr.hcl로 복사하고 실제 값으로 수정하세요

aws_region = "ap-northeast-2"  # AWS 리전
vpc_id     = "vpc-033b2d75131f80eff"    # VPC ID
subnet_id  = "subnet-0c0a58264893d46b0" # Public Subnet ID (AMI 빌드용, 인터넷 접근 필요)
# 주의: 이 AMI는 Public Subnet에서 빌드되지만, Private Subnet의 EC2에서 사용됩니다

# 소스 AMI ID (Ubuntu 22.04 LTS)
# 찾는 방법: AWS Console > EC2 > AMIs > Public images > ubuntu/images/hvm-ssd/ubuntu-jammy-22.04-amd64-server
source_ami_id = "ami-0c9c942bd7bf113a2"  # ap-northeast-2 Ubuntu 22.04 예시

instance_type  = "t3.micro"      # 빌드 시 사용할 인스턴스 타입
ssh_username   = "ubuntu"
ami_name_prefix = "anonymous-project-ami"

