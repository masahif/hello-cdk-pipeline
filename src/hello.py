
def handler(event, context):
    return {
        'statusCode': 200,
        'body': 'Hello CDK',
    }

if __name__ == "__main__":
    print(handler(None, None))