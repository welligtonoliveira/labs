# shellcheck disable=SC2006
filenames=`ls ./output/*.json`

for filename in $filenames
do
    echo $filename
    aws sqs send-message-batch --queue-url https://sqs.us-east-1.amazonaws.com/420458168333/integrator-vcom-enqueue-delete-installment-dlq --entries file://"$filename" --profile noverde-prd --region us-east-1 > /dev/null
    mv $filename ./output/enviados
done