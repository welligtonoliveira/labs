filenames=`ls ./output/*v2_*.json`

for filename in $filenames
do
    echo $filename
    aws sqs send-message-batch --queue-url https://sqs.us-east-1.amazonaws.com/420458168333/platform-loans-credit-analysis-queue --profile aws_prod --entries file://"$filename" --region us-east-1 > /dev/null
    mv $filename ./output/enviados
done