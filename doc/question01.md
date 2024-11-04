# Question 01

A development team lead is configuring policies for his team at an IT company.
Which of the following policy types only limit permissions but cannot grant permissions (Select two)?

1. Permissions boundary
2. Resource-based policy
3. Access control list (ACL)
4. Identity-based policy
5. AWS Organizations Service Control Policy (SCP)

## Domain: Security

### 01 - Permissions Boundary

#### Steps

##### Part 1
1. Create a managed policy allowing read-only access to IAM.
2. Create a user associated with the policy created in the last step as a permissions boundary.
3. Test if the user has access to list users (expected: no access).

   **Conclusion**: 🚫 Permissions Boundary does not allow access.

##### Part 2
1. Create a managed policy allowing full access to IAM.
2. Attach the managed policy created in the previous step to the user.
3. Test if the user has access to list users (expected: access limited by the permissions boundary).

   **Conclusion**: ✅ Even with a full access policy, the user is limited by the permissions boundary.

### 02 - Resource Based Policy

#### Steps

### 03 - ACL

#### Steps
1. Create two S3 buckets: one with a public read ACL and one without.
2. Create a user with a policy allowing read access to both S3 buckets.
3. Upload an object to both S3 buckets.
4. Test if the user has access to read objects from both buckets (expected: access granted only by the bucket with ACL).

   **Conclusion**: ✅ The user has access to read objects from the bucket with ACL but not from the bucket without ACL.

### 04 - Identity Based Policy

#### Steps

### 05 - AWS Organizations Service Control Policy (SCP)

#### Steps
