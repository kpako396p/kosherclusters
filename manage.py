from flask import Flask
from pymongo import MongoClient
from flask_restful import Resource, Api, reqparse
import datetime
import env
import os

app = Flask(__name__, instance_relative_config=True)
api = Api(app)

MONGO = env.BaseConfig.MONGO_URL


client = MongoClient(MONGO)
db = client.site
users = db.users

class CreatePool(Resource):
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('poolName', type=str, help='pool name', required=True)
        parser.add_argument('poolOwner', type=str, help='pool owner')
        
        args = parser.parse_args()
        
        class Pool:
            name = args['poolName']
            owner = args['poolOwner']
            time = str(datetime.datetime.now().time())
        
        NewPool = Pool()
        
        AddPool = users.update({'username': NewPool.owner}, 
                {'$push': 
                    {'pools':
                            {
                                'poolName': NewPool.name,
                                'poolCreateTime': NewPool.time,
                                'poolActive': 'yes',
                            }
                    }
                }
            )

        print ('New pool added with name: ', NewPool.name)
        return {'poolOwner': NewPool.owner,
                'poolName': NewPool.name,
                'poolDate': NewPool.time,
                }

api.add_resource(CreatePool, '/createpool')

class CreateNode(Resource):
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('nodeName', type=str, help='node name', required=True)
        parser.add_argument('poolName', type=str, help='pool name')
        parser.add_argument('owner', type=str, help='owner')
        
        args = parser.parse_args()
        
        class Node:
            pool = args['poolName']
            name = args['nodeName']
            owner = args['owner']
            
        node = Node()

        def pushToBase(node, pool, owner):
            users.update(
                {
                    'username': owner,
                },
                {'$push':
                    {'nodes':
                        {'$each':
                            [{
                                'name': node,
                                'state': 'off',
                                'pool': pool,
                            }]
                        }
                    }
                }
                ,upsert=True)
        pushToBase(node.name, node.pool, node.owner)
        
        def runNodeContainer(node, owner):
            tagging = 'sudo docker tag debian ' + owner + '/' + node
            running = 'sudo docker run -d -ti ' + owner + '/' + node
            os.system(tagging)
            print ('docker tag: ' + owner + '/' + node )
            os.system(running)
            print ('started node: ') 

        
        runNodeContainer(node.name,node.owner)

        return {'nodeName': node.name,
                'poolName': node.pool,
                'owner': node.owner
                }

api.add_resource(CreateNode, '/createnode')

class GetNodes(Resource):
    def get(self):
        parser = reqparse.RequestParser()
        parser.add_argument('owner', type=str, help='node owner')
        args = parser.parse_args()
        
        owner = args['owner']

        cursor = users.find({'username': owner}, { 'nodes.name': 1})
        nodes = {}
        nodesList = []
        for node in cursor:
            try:
                nodes['nodes'] = node['nodes']
            except:
                pass
        return nodes

api.add_resource(GetNodes, '/getnodes')


if __name__ == '__main__':
    app.run(debug=True,host='0.0.0.0', port=5002)
