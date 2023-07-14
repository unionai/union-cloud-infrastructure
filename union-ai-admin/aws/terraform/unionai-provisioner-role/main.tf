variable "role_name" {
  description = "The name of the IAM policy"
  type        = string
  default     = "unionai-manager-role"
}

resource "aws_iam_role" "provisioner_role" {
  name               = var.role_name
  assume_role_policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "AWS": "arn:aws:iam::479331373192:root"
      },
      "Action": "sts:AssumeRole"
    }
  ]
}
EOF
}

resource "aws_iam_managed_policy" "admin_policy" {
  name        = "unionai-admin-policy-for-manager-role"
  policy = file("../admin.json")
}

resource "aws_iam_managed_policy" "manager_policy" {
  name        = "unionai-manager-policy-for-manager-role"
  policy = file("../manager.json")
}

resource "aws_iam_managed_policy" "reader_policy" {
  name        = "unionai-reader-policy-for-manager-role"
  policy = file("../reader.json")
}

resource "aws_iam_role_policy_attachment" "provisioner_policy_attachment" {
  role       = aws_iam_role.provisioner_role.name
  policy_arn = aws_iam_managed_policy.read_policy.arn
}

resource "aws_iam_role_policy_attachment" "provisioner_manager_policy_attachment" {
  role       = aws_iam_role.provisioner_role.name
  policy_arn = aws_iam_managed_policy.manager_policy.arn
}

resource "aws_iam_role_policy_attachment" "admin_admin_policy_attachment" {
  role       = aws_iam_role.admin_role.name
  policy_arn = aws_iam_managed_policy.admin_policy.arn
}
