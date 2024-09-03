# shellcheck disable=SC2006
filenames=`ls ./output/*.json`

for filename in $filenames
do
    echo $filename
    aws sqs send-message-batch --queue-url https://sqs.us-east-1.amazonaws.com/420458168333/platform-risk-ph3a_v2-dlq --entries file://"$filename" --profile aws_prod --region us-east-1 > /dev/null
    mv $filename ./output/enviados
done