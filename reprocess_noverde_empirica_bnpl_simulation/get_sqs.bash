for i in {1..2}
do
  aws sqs receive-message --queue-url https://sqs.us-east-1.amazonaws.com/420458168333/platform-risk-subpopulation_policy-dlq --profile aws_prod --region us-east-1 --output json --attribute-names All --message-attribute-names All --max-number-of-messages 10 --wait-time-seconds 10 > "./input/$i".json
done