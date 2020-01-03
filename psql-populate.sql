
INSERT INTO "Venue" (name, address, city, state, phone, genres, website, seeking_talent, seeking_description, image_link, facebook_link) 
       VALUES ('The Musical Hop','1015 Folsom Street','San Francisco','CA','123-123-1234', ARRAY['Jazz', 'Reggae', 'Swing', 'Classical', 'Folk'], 'https://www.themusicalhop.com', True, 
              'We are on the lookout for a local artist to play every two weeks. Please call us.',
              'https://images.unsplash.com/photo-1543900694-133f37abaaa5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=400&q=60',
              'https://www.facebook.com/TheMusicalHop');


INSERT INTO "Venue" (name, address, city, state, phone, genres, website, seeking_talent, seeking_description, image_link, facebook_link) 
       VALUES ('The Dueling Pianos Bar',  '335 Delancey Street', 'New York', 'NY', '914-003-1132', ARRAY['Classical', 'R&B', 'Hip-Hop'], 'https://www.theduelingpianos.com', False, '',
              'https://images.unsplash.com/photo-1497032205916-ac775f0649ae?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=750&q=80',
			  'https://www.facebook.com/theduelingpianos');


INSERT INTO "Venue" (name, address, city, state, phone, genres, website, seeking_talent, seeking_description, image_link, facebook_link) 
       VALUES ('Park Square Live Music & Coffee','34 Whiskey Moore Ave', 'San Francisco', 'CA', '415-000-1234', ARRAY['Rock n Roll', 'Jazz', 'Classical', 'Folk'],
              'https://www.parksquarelivemusicandcoffee.com',False,'',
              'https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80',
              'https://www.facebook.com/ParkSquareLiveMusicAndCoffee');
 
 
INSERT INTO "Artist" (name, city, state, phone, website, genres, seeking_venue, seeking_description, image_link, facebook_link) 
       VALUES ('Guns N Petals','San Francisco','CA','326-123-5000','https://www.gunsnpetalsband.com',ARRAY['Rock n Roll'], True,
    		  'Looking for shows to perform at in the San Francisco Bay Area!',
    		  'https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80',
    		  'https://www.facebook.com/GunsNPetals');
   
 
INSERT INTO "Artist" (name, city, state, phone, website, genres, seeking_venue, seeking_description, image_link, facebook_link) 
       VALUES ('Matt Quevedo','New York','NY','300-400-5000','',ARRAY['Jazz'],False,'',
              'https://images.unsplash.com/photo-1495223153807-b916f75de8c5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=334&q=80',
              'https://www.facebook.com/mattquevedo923251523' );

INSERT INTO "Artist" (name, city, state, phone, website, genres, seeking_venue, seeking_description, image_link, facebook_link) 
       VALUES ('The Wild Sax Band','San Francisco','CA','432-325-5432','',ARRAY['Jazz', 'Classical'],False,'',
    		  'https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80',
    		  '');
   
INSERT INTO "Show" (venue_id, artist_id, start_time) 
       VALUES (1,1,'2019-05-21T21:30:00.000Z');
INSERT INTO "Show" (venue_id, artist_id, start_time) 
       VALUES (3,2,'2019-06-15T23:00:00.000Z');
INSERT INTO "Show" (venue_id, artist_id, start_time) 
       VALUES (3,3,'2035-04-01T20:00:00.000Z');
INSERT INTO "Show" (venue_id, artist_id, start_time) 
       VALUES (3,3,'2035-04-08T20:00:00.000Z');
INSERT INTO "Show" (venue_id, artist_id, start_time) 
       VALUES (3,3,'2035-04-15T20:00:00.000Z');
