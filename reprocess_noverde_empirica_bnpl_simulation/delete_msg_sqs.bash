# shellcheck disable=SC2006

for receipt_handle in $(cat ./ReceiptHandle_to_remove.txt)
do
    echo $receipt_handle
    aws sqs delete-message --queue-url https://sqs.us-east-1.amazonaws.com/420458168333/platform-risk-subpopulation_policy-dlq --profile aws_prod --region us-east-1  --receipt-handle $receipt_handle
done