filenames=`ls ./output/analyses_parent_2025_09_08_1654*.json`

for filename in $filenames
do
    echo $filename
    aws sqs send-message-batch --queue-url https://sqs.us-east-1.amazonaws.com/420458168333/platform-loans-settle-parent-loan-dlq --profile aws_prod --entries file://"$filename" --region us-east-1 > /dev/null
    mv $filename ./output/enviados
done