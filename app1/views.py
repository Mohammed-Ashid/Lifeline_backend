from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Feed, Person
from .serializers import FeedSerializer

class NewFeedView(APIView):
    def post(self, request):
        data = request.data
        print("Received data:", data)  # Debug log

        # Ensure user exists
        try:
            Person.objects.get(userId=data['user'])  # Just verify existence
        except Person.DoesNotExist:
            print(f"User with userId {data['user']} not found")
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)

        # Prepare data for the Feed model, pass user as the integer ID
        feed_data = {
            'type': data.get('type', 'donation'),
            'category': data['category'],
            'group': data.get('group'),
            'urgency': data['urgency'],
            'user': data['user'],  # Pass the integer userId directly
            'location': data['location'],
            'title': data['title'],
            'content': data['content'],
            'status': data.get('status', 'pending')
        }

        serializer = FeedSerializer(data=feed_data)
        if serializer.is_valid():
            serializer.save()
            print("Feed saved:", serializer.data)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        print("Validation errors:", serializer.errors)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

# ================== feed==========================
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Feed
from .serializers import FeedSerializerPending

class PendingFeedsView(APIView):
    def get(self, request):
        # Fetch all Feed objects with status="pending"
        pending_feeds = Feed.objects.filter(status='pending')
        serializer = FeedSerializerPending(pending_feeds, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    # ==========login/signup--------------------------------------
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.hashers import make_password, check_password
from .models import Person
import json

@csrf_exempt
def signup(request):
    if request.method == 'POST':
        try:
            # Handle multipart form data (username, password, idProof file)
            user_name = request.POST.get('userName')
            password = request.POST.get('password')
            id_proof = request.FILES.get('idProof')

            if not user_name or not password:
                return JsonResponse({'status': 'error', 'message': 'Username and password are required.'}, status=400)

            if Person.objects.filter(userName=user_name).exists():
                return JsonResponse({'status': 'error', 'message': 'Username already exists.'}, status=400)

            if len(password) < 6:
                return JsonResponse({'status': 'error', 'message': 'Password must be at least 6 characters.'}, status=400)

            # Create new Person instance
            person = Person(
                userName=user_name,
                password=make_password(password),  # Hash the password
                idProof=id_proof if id_proof else None,
                role='User',  # Default role
                status='Active'  # Default status
            )
            person.save()

            return JsonResponse({
                'status': 'success',
                'message': 'Account created successfully! Please verify your email.',
                'userId': person.userId
            }, status=201)

        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

    return JsonResponse({'status': 'error', 'message': 'Invalid method'}, status=405)

@csrf_exempt
def login(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            user_name = data.get('userName')
            password = data.get('password')

            if not user_name or not password:
                return JsonResponse({'status': 'error', 'message': 'Username and password are required.'}, status=400)

            try:
                person = Person.objects.get(userName=user_name)
            except Person.DoesNotExist:
                return JsonResponse({'status': 'error', 'message': 'Invalid username or password.'}, status=401)

            if not check_password(password, person.password):
                return JsonResponse({'status': 'error', 'message': 'Invalid username or password.'}, status=401)

            if person.status != 'Active':
                return JsonResponse({'status': 'error', 'message': 'Account is inactive. Please contact support.'}, status=403)

            return JsonResponse({
                'status': 'success',
                'message': 'Login successful! Welcome back.',
                'userId': person.userId,
                'role': person.role
            }, status=200)

        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

    return JsonResponse({'status': 'error', 'message': 'Invalid method'}, status=405)

# ======================messages============================
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Feed, Person, FeedRequest
import json

@csrf_exempt
def make_request(request):
    if request.method == 'POST':
        try:
            # Parse the incoming JSON data from the Connect component
            data = json.loads(request.body)
            feed_id = data.get('feedId')  # Maps to feedId in FeedRequest
            user_id = data.get('userId')  # Maps to secondPersonId in FeedRequest
            message = data.get('message')  # Optional field, not saved unless added to model

            # Validate required fields
            if not feed_id or not user_id:
                return JsonResponse({'status': 'error', 'message': 'feedId and userId are required.'}, status=400)

            # Fetch the related Feed and Person objects
            try:
                feed = Feed.objects.get(id=feed_id)
            except Feed.DoesNotExist:
                return JsonResponse({'status': 'error', 'message': 'Feed not found.'}, status=404)

            try:
                person = Person.objects.get(userId=user_id)
            except Person.DoesNotExist:
                return JsonResponse({'status': 'error', 'message': 'User not found.'}, status=404)

            # Create and save the FeedRequest instance
            feed_request = FeedRequest(
                feedId=feed,           # Foreign key to Feed
                secondPersonId=person, # Foreign key to Person
                message=message,
                status='Pending'       # Default status
            )
            feed_request.save()

            return JsonResponse({
                'status': 'success',
                'message': 'Request created successfully.',
                'requestId': feed_request.id
            }, status=201)

        except json.JSONDecodeError:
            return JsonResponse({'status': 'error', 'message': 'Invalid JSON data.'}, status=400)
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

    return JsonResponse({'status': 'error', 'message': 'Invalid method. Use POST.'})


# ==========================notification===============================================
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Feed, FeedRequest, Person
import json

@csrf_exempt
def get_user_notifications(request):
    if request.method == 'POST':
        try:
            # Parse the incoming JSON data
            data = json.loads(request.body)
            user_id = data.get('userId')
            print("User ID:", user_id)  # Debugging

            if not user_id:
                return JsonResponse({'status': 'error', 'message': 'userId is required.'}, status=400)

            # Fetch pending feeds for the user
            pending_feeds = Feed.objects.filter(user__userId=user_id, status='pending')
            print("Pending Feeds:", pending_feeds)  # Debugging

            if not pending_feeds.exists():
                return JsonResponse({'status': 'success', 'data': [], 'message': 'No pending feeds found.'}, status=200)

            # Build the notification data
            notifications = []
            for feed in pending_feeds:
                # Fetch related feed requests with status 'Pending' only
                feed_requests = FeedRequest.objects.filter(feedId=feed, status='Pending')
                print("Pending Feed Requests for Feed", feed.id, ":", feed_requests)  # Debugging

                for request in feed_requests:
                    second_person = request.secondPersonId
                    notifications.append({
                        'feed': {
                            'id': feed.id,
                            'title': feed.title,
                            'type': feed.type,
                            'category': feed.category,
                            'urgency': feed.urgency,
                            'content': feed.content,
                            'time_posted': feed.time_posted.isoformat(),
                            'location': feed.location,
                        },
                        'request': {
                            'id': request.id,
                            'status': request.status,
                            'requestedDate': request.requestedDate.isoformat(),
                            'message': request.message,
                        },
                        'secondPerson': {
                            'userId': second_person.userId,
                            'userName': second_person.userName,
                            'role': second_person.role,
                            'status': second_person.status,
                        }
                    })

            return JsonResponse({
                'status': 'success',
                'data': notifications,
                'message': 'Notifications retrieved successfully.'
            }, status=200)

        except Person.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'User not found.'}, status=404)
        except json.JSONDecodeError:
            return JsonResponse({'status': 'error', 'message': 'Invalid JSON data.'}, status=400)
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

    return JsonResponse({'status': 'error', 'message': 'Invalid method. Use POST.'}, status=405)



# ====================================Notification==========================================
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import FeedRequest
import json

@csrf_exempt
def accept_notification(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            request_id = data.get('requestId')
            email = data.get('email')
            phone = data.get('phone')

            if not request_id:
                return JsonResponse({'status': 'error', 'message': 'requestId is required.'}, status=400)
            if not email or not phone:
                return JsonResponse({'status': 'error', 'message': 'Email and phone number are required.'}, status=400)

            try:
                feed_request = FeedRequest.objects.get(id=request_id)
                if feed_request.status != 'Pending':
                    return JsonResponse({'status': 'error', 'message': 'Request already processed.'}, status=400)

                # Append email and phone to the existing message
                current_message = feed_request.message or ''  # Use empty string if message is None
                updated_message = f"{current_message}\nContact Details: Email: {email}, Phone: {phone}".strip()
                feed_request.message = updated_message

                # Update the status
                feed_request.status = 'Approved'
                feed_request.save()

                # Log for debugging (optional)
                print(f"Updated message for request {request_id}: {updated_message}")

                return JsonResponse({
                    'status': 'success',
                    'message': 'Notification accepted successfully.',
                    'requestId': feed_request.id
                }, status=200)
            except FeedRequest.DoesNotExist:
                return JsonResponse({'status': 'error', 'message': 'Notification not found.'}, status=404)

        except json.JSONDecodeError:
            return JsonResponse({'status': 'error', 'message': 'Invalid JSON data.'}, status=400)
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

    return JsonResponse({'status': 'error', 'message': 'Invalid method. Use POST.'}, status=405)

@csrf_exempt
def reject_notification(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            request_id = data.get('requestId')
            print(request_id)

            if not request_id:
                return JsonResponse({'status': 'error', 'message': 'requestId is required.'}, status=400)

            try:
                feed_request = FeedRequest.objects.get(id=request_id)
                if feed_request.status != 'Pending':
                    return JsonResponse({'status': 'error', 'message': 'Request already processed.'}, status=400)
                
                feed_request.status = 'Rejected'
                feed_request.save()
                return JsonResponse({
                    'status': 'success',
                    'message': 'Notification rejected successfully.',
                    'requestId': feed_request.id
                }, status=200)
            except FeedRequest.DoesNotExist:
                return JsonResponse({'status': 'error', 'message': 'Notification not found.'}, status=404)

        except json.JSONDecodeError:
            return JsonResponse({'status': 'error', 'message': 'Invalid JSON data.'}, status=400)
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

    return JsonResponse({'status': 'error', 'message': 'Invalid method. Use POST.'}, status=405)

# ==========================================accepted request=============================
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Feed, FeedRequest, Person
import json

@csrf_exempt
def get_approved_requests(request):
    if request.method == 'POST':
        try:
            # Parse the incoming JSON data
            data = json.loads(request.body)
            user_id = data.get('userId')
            print("User ID:", user_id)  # Debugging

            if not user_id:
                return JsonResponse({'status': 'error', 'message': 'userId is required.'}, status=400)

            # Fetch approved feed requests where the user is the secondPersonId
            approved_requests = FeedRequest.objects.filter(secondPersonId__userId=user_id, status='Approved')
            print("Approved Requests:", approved_requests)  # Debugging

            if not approved_requests.exists():
                return JsonResponse({'status': 'success', 'data': [], 'message': 'No approved requests found.'}, status=200)

            # Build the response data
            approved_data = []
            for request in approved_requests:
                feed = request.feedId
                posted_user = feed.user  # The user who posted the feed
                approved_data.append({
                    'request': {
                        'id': request.id,
                        'status': request.status,
                        'requestedDate': request.requestedDate.isoformat(),
                        'message': request.message,
                    },
                    'feed': {
                        'id': feed.id,
                        'title': feed.title,
                        'type': feed.type,
                        'category': feed.category,
                        'urgency': feed.urgency,
                        'content': feed.content,
                        'time_posted': feed.time_posted.isoformat(),
                        'location': feed.location,
                        'status': feed.status,
                    },
                    'postedUser': {
                        'userId': posted_user.userId,
                        'userName': posted_user.userName,
                        'role': posted_user.role,
                        'status': posted_user.status,
                    }
                })

            return JsonResponse({
                'status': 'success',
                'data': approved_data,
                'message': 'Approved requests retrieved successfully.'
            }, status=200)

        except Person.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'User not found.'}, status=404)
        except json.JSONDecodeError:
            return JsonResponse({'status': 'error', 'message': 'Invalid JSON data.'}, status=400)
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

    return JsonResponse({'status': 'error', 'message': 'Invalid method. Use POST.'}, status=405)
from rest_framework.decorators import api_view
from .serializers import PersonSerializer
@api_view(['GET'])
def get_user_by_id(request, user_id):
    try:
        user = Person.objects.get(userId=user_id)
        serializer = PersonSerializer(user)
        print(serializer.data)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except Person.DoesNotExist:
        return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)