from flask import Flask
from pymongo import MongoClient
from flask_restful import Resource, Api, reqparse
import datetime
import env

app = Flask(__name__, instance_relative_config=True)
api = Api(app)

MONGO = env.BaseConfig.MONGO_URL


client = MongoClient(MONGO)
db = client.site
posts = db.posts
users = db.users

print (" * MONGO_IP: ", MONGO)

class CreatePost(Resource):
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('name', type=str, help='Post name', required=True)
        parser.add_argument('text', type=str, help='Post text')
        parser.add_argument('author', type=str, help='Post author')
        
        args = parser.parse_args()
        
        class Post:
            name = args['name']
            text = args['text']
            author = args['author']
            time = str(datetime.datetime.now().time())

        NewPost = Post()
        
        AddPost = posts.insert_one({
            'name': NewPost.name,
            'text': NewPost.text,
            'time': NewPost.time,
            'author': NewPost.author,
            'show': 'yes',
            })

        print ('New post added with name: ', NewPost.name)
        return {'Name': NewPost.name,
                'Text': NewPost.text,
                'Date': NewPost.time,
                'Author': NewPost.author
                }

api.add_resource(CreatePost, '/createpost')

class GetPosts(Resource):
    def get(self):
        
        cursor = posts.find({'show': 'yes'})
        postsList = []
        for post in cursor:
            postsList.append({
                'name': post['name'],
                'text': post['text'],
                'time': post['time'],
                'author': post['author'],
                })
        return postsList

api.add_resource(GetPosts, '/getposts')

class UserRegistration(Resource):
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('username', type=str, help='username', required=True)
        parser.add_argument('password', type=str, help='password')
        parser.add_argument('email', type=str, help='email')
        
        args = parser.parse_args()
        
        class User:
            username = args['username']
            password = args['password']
            email = args['email']

        NewUser = User()
        
        AddUser = users.insert_one({
            'username': NewUser.username,
            'password': NewUser.password,
            'email': NewUser.email,
            })

        print ('New user added with name: ', NewUser.username)
        return {'username': NewUser.username,
                'password': NewUser.password,
                'email': NewUser.email,
                }

api.add_resource(UserRegistration, '/registration')


class Login(Resource):
    def get(self):
        
        parser = reqparse.RequestParser()
        parser.add_argument('username', type=str, help='username', required=True)
        parser.add_argument('password', type=str, help='password')
        
        args = parser.parse_args()
        cursor = users.find({'username': args['username']})
    
        checkExist = cursor.count()

        if checkExist == 0:
            return {'status': 404}
        else:
            for doc in cursor:
                if doc['password'] == args['password']:
                    return {'status': 200}
                else: 
                    return {'status': 403}

api.add_resource(Login, '/login')


if __name__ == '__main__':
    app.run(debug=True,host='0.0.0.0')
