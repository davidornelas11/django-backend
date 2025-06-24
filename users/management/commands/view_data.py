from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from users.models import Profile, EmailVerification, RefreshToken
from django.utils import timezone
import json

class Command(BaseCommand):
    help = 'View database data in a clean, readable format'

    def add_arguments(self, parser):
        parser.add_argument(
            '--users',
            action='store_true',
            help='Show all users and their profiles',
        )
        parser.add_argument(
            '--profiles',
            action='store_true',
            help='Show detailed profile information',
        )
        parser.add_argument(
            '--meal-plans',
            action='store_true',
            help='Show generated meal plans',
        )
        parser.add_argument(
            '--user',
            type=str,
            help='Show data for specific user (username)',
        )
        parser.add_argument(
            '--summary',
            action='store_true',
            help='Show database summary statistics',
        )

    def handle(self, *args, **options):
        if options['summary']:
            self.show_summary()
        elif options['users']:
            self.show_users()
        elif options['profiles']:
            self.show_profiles()
        elif options['meal_plans']:
            self.show_meal_plans()
        elif options['user']:
            self.show_user_detail(options['user'])
        else:
            self.show_help()

    def show_help(self):
        self.stdout.write(self.style.SUCCESS('🗄️  Database Viewer Commands:'))
        self.stdout.write('')
        self.stdout.write('  python manage.py view_data --summary      # Database overview')
        self.stdout.write('  python manage.py view_data --users        # All users')
        self.stdout.write('  python manage.py view_data --profiles     # All profiles')
        self.stdout.write('  python manage.py view_data --meal-plans   # Generated meal plans')
        self.stdout.write('  python manage.py view_data --user <name>  # Specific user details')
        self.stdout.write('')

    def show_summary(self):
        self.stdout.write(self.style.SUCCESS('📊 Database Summary'))
        self.stdout.write('=' * 50)
        
        total_users = User.objects.count()
        verified_users = User.objects.filter(email_verification__is_verified=True).count()
        profiles_with_meal_plans = Profile.objects.filter(meal_plan__isnull=False).count()
        
        self.stdout.write(f'👥 Total Users: {total_users}')
        self.stdout.write(f'✅ Verified Users: {verified_users}')
        self.stdout.write(f'🍽️  Profiles with Meal Plans: {profiles_with_meal_plans}')
        self.stdout.write('')
        
        # Profile status breakdown
        statuses = Profile.objects.values_list('status', flat=True)
        status_counts = {}
        for status in statuses:
            status_counts[status] = status_counts.get(status, 0) + 1
        
        self.stdout.write('📈 Profile Status Breakdown:')
        for status, count in status_counts.items():
            self.stdout.write(f'   {status}: {count}')

    def show_users(self):
        self.stdout.write(self.style.SUCCESS('👥 All Users'))
        self.stdout.write('=' * 80)
        
        users = User.objects.select_related('profile', 'email_verification').all()
        
        for user in users:
            email_verified = '✅' if hasattr(user, 'email_verification') and user.email_verification.is_verified else '❌'
            profile_status = user.profile.status if hasattr(user, 'profile') else 'No Profile'
            has_meal_plan = '🍽️' if hasattr(user, 'profile') and user.profile.meal_plan else '⭕'
            
            self.stdout.write(
                f'{user.username:<20} | {user.email:<30} | {email_verified} | {profile_status:<12} | {has_meal_plan}'
            )

    def show_profiles(self):
        self.stdout.write(self.style.SUCCESS('👤 User Profiles'))
        self.stdout.write('=' * 100)
        
        profiles = Profile.objects.select_related('user').all()
        
        for profile in profiles:
            self.stdout.write(f'\n🔸 {profile.user.username} ({profile.user.email})')
            self.stdout.write(f'   Status: {profile.status}')
            self.stdout.write(f'   Location: {profile.location or "Not set"}')
            self.stdout.write(f'   Budget: ${profile.weekly_budget or "Not set"}')
            self.stdout.write(f'   Created: {profile.created_at.strftime("%Y-%m-%d %H:%M")}')
            
            if profile.preferences:
                self.stdout.write(f'   Preferences: {json.dumps(profile.preferences, indent=6)}')
            
            if profile.dietary_restrictions:
                self.stdout.write(f'   Dietary Restrictions: {json.dumps(profile.dietary_restrictions, indent=6)}')
            
            if profile.meal_plan:
                self.stdout.write(f'   🍽️  Has Meal Plan: Yes')
                if 'cart_url' in profile.meal_plan:
                    self.stdout.write(f'   🛒 Cart URL: {profile.meal_plan["cart_url"]}')

    def show_meal_plans(self):
        self.stdout.write(self.style.SUCCESS('🍽️  Generated Meal Plans'))
        self.stdout.write('=' * 80)
        
        profiles_with_plans = Profile.objects.filter(meal_plan__isnull=False).select_related('user')
        
        if not profiles_with_plans:
            self.stdout.write('No meal plans found.')
            return
        
        for profile in profiles_with_plans:
            self.stdout.write(f'\n🔸 {profile.user.username}')
            self.stdout.write(f'   Status: {profile.status}')
            self.stdout.write(f'   Updated: {profile.updated_at.strftime("%Y-%m-%d %H:%M")}')
            
            meal_plan = profile.meal_plan
            if 'cart_url' in meal_plan:
                self.stdout.write(f'   🛒 Cart URL: {meal_plan["cart_url"]}')
            
            if 'plan' in meal_plan:
                plan_preview = meal_plan['plan'][:200] + '...' if len(meal_plan['plan']) > 200 else meal_plan['plan']
                self.stdout.write(f'   📝 Plan Preview: {plan_preview}')

    def show_user_detail(self, username):
        try:
            user = User.objects.select_related('profile', 'email_verification', 'refresh_token').get(username=username)
        except User.DoesNotExist:
            self.stdout.write(self.style.ERROR(f'User "{username}" not found.'))
            return
        
        self.stdout.write(self.style.SUCCESS(f'👤 User Details: {username}'))
        self.stdout.write('=' * 60)
        
        # Basic user info
        self.stdout.write(f'Username: {user.username}')
        self.stdout.write(f'Email: {user.email}')
        self.stdout.write(f'First Name: {user.first_name or "Not set"}')
        self.stdout.write(f'Last Name: {user.last_name or "Not set"}')
        self.stdout.write(f'Date Joined: {user.date_joined.strftime("%Y-%m-%d %H:%M")}')
        self.stdout.write(f'Is Staff: {"Yes" if user.is_staff else "No"}')
        
        # Email verification
        if hasattr(user, 'email_verification'):
            ev = user.email_verification
            self.stdout.write(f'\n📧 Email Verification:')
            self.stdout.write(f'   Verified: {"✅ Yes" if ev.is_verified else "❌ No"}')
            self.stdout.write(f'   Created: {ev.created_at.strftime("%Y-%m-%d %H:%M")}')
            self.stdout.write(f'   Expires: {ev.expires_at.strftime("%Y-%m-%d %H:%M")}')
            self.stdout.write(f'   Expired: {"Yes" if ev.is_expired() else "No"}')
        
        # Profile
        if hasattr(user, 'profile'):
            profile = user.profile
            self.stdout.write(f'\n👤 Profile:')
            self.stdout.write(f'   Status: {profile.status}')
            self.stdout.write(f'   Bio: {profile.bio or "Not set"}')
            self.stdout.write(f'   Location: {profile.location or "Not set"}')
            self.stdout.write(f'   Budget: ${profile.weekly_budget or "Not set"}')
            
            if profile.preferences:
                self.stdout.write(f'   Preferences: {json.dumps(profile.preferences, indent=6)}')
            
            if profile.dietary_restrictions:
                self.stdout.write(f'   Dietary Restrictions: {json.dumps(profile.dietary_restrictions, indent=6)}')
            
            if profile.meal_plan:
                self.stdout.write(f'\n🍽️  Meal Plan:')
                meal_plan = profile.meal_plan
                if 'cart_url' in meal_plan:
                    self.stdout.write(f'   Cart URL: {meal_plan["cart_url"]}')
                if 'generated_at' in meal_plan:
                    self.stdout.write(f'   Generated: {meal_plan["generated_at"]}')
                if 'plan' in meal_plan:
                    self.stdout.write(f'   Plan Content: {meal_plan["plan"][:500]}...') 