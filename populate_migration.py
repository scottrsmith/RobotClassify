
from datetime import datetime

    
# Add Records for default data
op.bulk_insert(
    Artist,
    [
    	{
           'name': 'Guns N Petals',
    	   'city': 'San Francisco',
    	   'state': 'CA',
    	   'phone': '326-123-5000',
    	   'website': 'https://www.gunsnpetalsband.com',
    	   'genres': ['Rock n Roll'], 
    	   'seeking_venue': True,
           'seeking_description': 'Looking for shows to perform at in the San Francisco Bay Area!',     	
    	   'image_link': 'https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80',
           'facebook_link':'https://www.facebook.com/GunsNPetals'
    	},
    	{
           'name': 'Matt Quevedo',
    	   'city': 'New York',
    	   'state': 'NY',
    	   'phone': '300-400-5000',
    	   'website': '',
    	   'genres': ['Jazz'], 
    	   'seeking_venue': False,
           'seeking_description': '',     	
    	   'image_link': 'https://images.unsplash.com/photo-1495223153807-b916f75de8c5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=334&q=80',
           'facebook_link':'https://www.facebook.com/mattquevedo923251523'
    	},
    	{
           'name': 'The Wild Sax Band',
    	   'city': 'San Francisco',
    	   'state': 'CA',
    	   'phone': '432-325-5432',
    	   'website': '',
    	   'genres': ['Jazz', 'Classical'], 
    	   'seeking_venue': False,
           'seeking_description': '',     	
    	   'image_link': 'https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80',
           'facebook_link':''
    	}
    ]
)


op.bulk_insert(
    Venue,
    [

     {
      'name': 'The Musical Hop',
      'address': '1015 Folsom Street',
      'city': 'San Francisco',
      'state': 'CA',
      'phone': '123-123-1234',
      'genres': ['Jazz', 'Reggae', 'Swing', 'Classical', 'Folk'],
      'website': 'https://www.themusicalhop.com',
      'seeking_talent': True,
      'seeking_description': 'We are on the lookout for a local artist to play every two weeks. Please call us.',
      'image_link': 'https://images.unsplash.com/photo-1543900694-133f37abaaa5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=400&q=60',
      'facebook_link': 'https://www.facebook.com/TheMusicalHop'
     },

     {
      'name': 'The Dueling Pianos Bar',
      'address': '335 Delancey Street',
      'city': 'New York',
      'state': 'NY',
      'phone': '914-003-1132',
      'genres': ['Classical', 'R&B', 'Hip-Hop'],
      'website': 'https://www.theduelingpianos.com',
      'seeking_talent': False,
      'seeking_description': '',
      'image_link': 'https://images.unsplash.com/photo-1497032205916-ac775f0649ae?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=750&q=80',
      'facebook_link':'https://www.facebook.com/theduelingpianos'
     },

     {
      'name': 'Park Square Live Music & Coffee',
      'address': '34 Whiskey Moore Ave',
      'city': 'San Francisco',
      'state': 'CA',
      'phone': '415-000-1234',
      'genres': ['Rock n Roll', 'Jazz', 'Classical', 'Folk'],
      'website': 'https://www.parksquarelivemusicandcoffee.com',
      'seeking_talent': False,
      'seeking_description': '',
      'image_link': 'https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80',
      'facebook_link': 'https://www.facebook.com/ParkSquareLiveMusicAndCoffee' 
     }
    ]
)


op.bulk_insert(
    Show,
    [
     {
      'venue_id': 1, 
      'artist_id': 1, 
      'start_time': datetime(2019,5,21,21,30,0)
     },
     {
      'venue_id': 3, 
      'artist_id': 2, 
      'start_time': datetime(2019,6,15,23,0,0)
     },
     {
      'venue_id': 3, 
      'artist_id': 3, 
      'start_time': datetime(2035,4,1,20,0,0)
     },
     {
      'venue_id': 3, 
      'artist_id': 3, 
      'start_time': datetime(2035,4,8,20,0,0)
     },
     {
      'venue_id': 3, 
      'artist_id': 3, 
      'start_time': datetime(2035,4,15,20,0,0)
     }   
    ]
)
  
