packer {
  required_plugins {
    amazon = {
      source  = "github.com/hashicorp/amazon"
      version = "~> 1"
    }
  }
}

variable "aws_region" {
  type        = string
  description = "AWS 리전 (예: ap-northeast-2)"
  default     = "ap-northeast-2"
}

variable "vpc_id" {
  type        = string
  description = "빌드할 때 사용할 VPC ID (Public Subnet이 속한 VPC)"
}

variable "subnet_id" {
  type        = string
  description = "빌드할 때 사용할 Subnet ID (Public Subnet - 인터넷 접근 필요)"
}

variable "source_ami_id" {
  type        = string
  description = "소스 AMI ID (Ubuntu 22.04 LTS 권장). 빈 문자열이면 자동으로 최신 Ubuntu 22.04를 찾습니다."
  default     = ""
  # Ubuntu 22.04 LTS 예시: ami-0c9c942bd7bf113a2 (ap-northeast-2)
}

variable "instance_type" {
  type        = string
  description = "빌드 시 사용할 EC2 인스턴스 타입"
  default     = "t3.micro"
}

variable "ssh_username" {
  type        = string
  description = "SSH 사용자명"
  default     = "ubuntu"
}

variable "ami_name_prefix" {
  type        = string
  description = "생성될 AMI 이름 접두사"
  default     = "anonymous-project-ami"
}

# AWS AMI 빌드 설정
source "amazon-ebs" "anonymous_project" {
  ami_name      = "${var.ami_name_prefix}-${formatdate("YYYYMMDD-hhmm", timestamp())}"
  instance_type = var.instance_type
  region        = var.aws_region

  # VPC 및 Subnet 설정
  # Public Subnet에서 빌드 (인터넷 접근 필요)
  # 생성된 AMI는 Private Subnet의 EC2에서 사용
  vpc_id            = var.vpc_id
  subnet_id         = var.subnet_id
  associate_public_ip_address = true  # Public Subnet에서 빌드하므로 true

  # AMI 소스 (Ubuntu)
  # source_ami_id 변수가 지정되면 사용, 아니면 필터로 찾기
  source_ami = var.source_ami_id != "" ? var.source_ami_id : null
  
  dynamic "source_ami_filter" {
    for_each = var.source_ami_id == "" ? [1] : []
    content {
      filters = {
        name                = "ubuntu/images/hvm-ssd/ubuntu-jammy-22.04-amd64-server-*"
        root-device-type    = "ebs"
        virtualization-type = "hvm"
      }
      most_recent = true
      owners      = ["099720109477"]  # Canonical (Ubuntu 공식 계정)
    }
  }

  ssh_username = var.ssh_username

  # IAM Instance Profile (필요한 권한이 있는 Role)
  # EC2가 S3, CodeDeploy 등에 접근할 수 있는 권한 필요
  # 주의: 실제 Role 이름으로 변경하거나 주석 처리하고 기본 Role 사용
  # iam_instance_profile = "packer-build-role"

  # SSH 접근을 위한 보안 그룹 설정
  # Public Subnet: 인터넷에서 접근 가능하도록 설정
  # 보안을 위해 특정 IP만 허용하려면 CIDR 블록을 변경하세요
  temporary_security_group_source_cidr = "0.0.0.0/0"  # Public Subnet이므로 인터넷 접근 허용

  # User data로 초기 설정 (선택사항)
  # user_data_file = "packer/user-data.sh"

  tags = {
    Name        = "anonymous-project-ami"
    Environment = "production"
    Project     = "anonymous-project"
    BuiltBy     = "packer"
  }
}

# 빌드 프로세스
build {
  name = "anonymous-project-ami"

  sources = [
    "source.amazon-ebs.anonymous_project"
  ]

  # 1. 시스템 업데이트 및 기본 패키지 설치
  provisioner "shell" {
    script = "packer/scripts/01-base-setup.sh"
  }

  # 2. Python 3 및 pip 설치
  provisioner "shell" {
    script = "packer/scripts/02-python-setup.sh"
  }

  # 3. CodeDeploy Agent 설치
  provisioner "shell" {
    script = "packer/scripts/03-codedeploy-agent.sh"
  }

  # 4. Nginx 설치 및 설정
  provisioner "shell" {
    script = "packer/scripts/04-nginx-setup.sh"
  }

  # 5. MariaDB Client 설치 (RDS 사용 시)
  provisioner "shell" {
    script = "packer/scripts/05-mariadb-client.sh"
  }

  # 6. Supervisor 설치 (프로세스 관리용)
  provisioner "shell" {
    script = "packer/scripts/06-supervisor-setup.sh"
  }

  # 7. 디렉토리 구조 생성 및 권한 설정
  provisioner "shell" {
    script = "packer/scripts/07-directories-setup.sh"
  }

  # 8. 환경 변수 및 설정 파일 복사
  provisioner "file" {
    source      = "packer/configs/"
    destination = "/tmp/packer-configs/"
  }

  # 9. 최종 정리 및 최적화
  provisioner "shell" {
    script = "packer/scripts/08-cleanup.sh"
  }

  # Post-processors (선택사항)
  post-processor "manifest" {
    output     = "packer-manifest.json"
    strip_path = true
  }
}

