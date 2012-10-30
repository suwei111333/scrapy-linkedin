Mongodb Scheme(**draft**)

---

**PersonProfile**

	PersonProfile
	{
		linkedin_id:'id',
		locality:'beijing',
		industry:'Research',
		summary:'I am a professor…',
		
		skills:
				[
					'data mining',
					'machine learning'
				],
				
		interests:
				[
					'data mining',
					'machine learning'
				],
				
		groups:
				[
					'acm',
					'ieee'
				],
				
		honors:
				[
					'first prize',
				],
		
		education:
				[
					{
						school_name: 'a'
						period: '1991-2012'
					},
				],
				
		experience:
				[
					{
						title:'associate professor',
						organization:'tsinghua',
						period:'1999-2000',
						description:'research about data mining',
					},
				],
				
		also_view:
				[
					{
						'linkedin_id':'asd',
						'url':'http',
					}
				],
		
	}