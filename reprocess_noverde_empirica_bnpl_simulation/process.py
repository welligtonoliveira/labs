import os
import json
from uuid import uuid4

directory = "./input"
target = "./output/"
count = 0
count_file = 0
lst_arqs = os.listdir(directory)
lst_arqs.sort()
result_receipt_handle = []
for filename in lst_arqs:
    result = []
    if filename.endswith('.json'):
        with open(os.path.join(directory, filename)) as f:
            print(filename)
            count_file += 1
            content = f.read()
            content = json.loads(content)

            for message in content["Messages"]:
                body = json.loads(message["Body"])
                result_receipt_handle.append(message["ReceiptHandle"])

                message_content = {"Id": str(uuid4())}
                message_content["MessageBody"] = json.dumps(body)
                result.append(message_content)


                count += 1
            print(count)

        print("End", count, count_file)
        result_file = open(target + filename, "x")
        result_file.write(json.dumps(result))
        result_file.close()

result_receipt = open("ReceiptHandle_to_remove.txt", "w")
result_receipt.write("\n".join(result_receipt_handle))
result_receipt.close()