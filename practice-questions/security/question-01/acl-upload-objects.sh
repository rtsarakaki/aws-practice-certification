#!/bin/bash

# Nome da conta AWS
ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)

# Nomes dos buckets
BUCKET_WITH_ACL=example-bucket-with-acl-$ACCOUNT_ID
BUCKET_WITHOUT_ACL=example-bucket-without-acl-$ACCOUNT_ID
OBJECT_NAME=test-file.txt

# Função para verificar se o objeto já existe no bucket
function object_exists {
  aws s3api head-object --bucket $1 --key $2 > /dev/null 2>&1
}

# Configura OwnershipControls para permitir ACLs no bucket com ACL
aws s3api put-bucket-ownership-controls --bucket $BUCKET_WITH_ACL --ownership-controls 'Rules=[{ObjectOwnership=ObjectWriter}]'

# Cria um arquivo de exemplo para fazer upload
echo "This is a test file" > $OBJECT_NAME

# Verifica se o objeto já existe no bucket com ACL
if object_exists $BUCKET_WITH_ACL $OBJECT_NAME; then
  echo "Objeto $OBJECT_NAME já existe no bucket $BUCKET_WITH_ACL. Não será feito upload."
else
  # Faz o upload do arquivo para o bucket com ACL, definindo ACLs no objeto
  aws s3 cp $OBJECT_NAME s3://$BUCKET_WITH_ACL/ --acl public-read
fi

# Verifica se o objeto já existe no bucket sem ACL
if object_exists $BUCKET_WITHOUT_ACL $OBJECT_NAME; then
  echo "Objeto $OBJECT_NAME já existe no bucket $BUCKET_WITHOUT_ACL. Não será feito upload."
else
  # Faz o upload do arquivo para o bucket sem ACL
  aws s3 cp $OBJECT_NAME s3://$BUCKET_WITHOUT_ACL/
fi

# Apaga o arquivo criado
rm $OBJECT_NAME