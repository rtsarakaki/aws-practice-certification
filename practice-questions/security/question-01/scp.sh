#!/bin/bash

# Get the target account ID from environment variables
TARGET_ACCOUNT_ID=$TARGET_ACCOUNT_ID

# Check if the organization already exists
ORG_STATUS=$(aws organizations describe-organization --query 'Organization.Id' --output text 2>&1)

if [[ $ORG_STATUS == *"AWSOrganizationsNotInUseException"* ]]; then
  echo "Creating organization..."
  aws organizations create-organization --feature-set ALL
else
  echo "Organization already exists. Skipping creation."
fi

# Check if the account is already part of the organization
ACCOUNT_STATUS=$(aws organizations list-accounts --query "Accounts[?Id=='$TARGET_ACCOUNT_ID'].Status" --output text)

if [[ $ACCOUNT_STATUS == "ACTIVE" ]]; then
  echo "Account $TARGET_ACCOUNT_ID is already part of the organization. Skipping invitation."
else
  echo "Inviting account $TARGET_ACCOUNT_ID to the organization..."
  INVITATION=$(aws organizations invite-account-to-organization --target Id=$TARGET_ACCOUNT_ID,Type=ACCOUNT --notes "Invitation to join organization")
  HANDSHAKE_ID=$(echo $INVITATION | jq -r '.Handshake.Id')

  # Save the handshake ID for future reference
  echo "HANDSHAKE_ID=$HANDSHAKE_ID" >> $GITHUB_ENV
fi