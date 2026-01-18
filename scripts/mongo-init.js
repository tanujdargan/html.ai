// MongoDB initialization script
// Creates indexes and initial data for html.ai

db = db.getSiblingDB('html_ai');

// Create indexes for businesses collection
db.businesses.createIndex({ "api_key": 1 }, { unique: true });
db.businesses.createIndex({ "business_id": 1 }, { unique: true });
db.businesses.createIndex({ "domain": 1 });

// Create indexes for global_users collection
db.global_users.createIndex({ "global_uid": 1 }, { unique: true });
db.global_users.createIndex({ "business_uids": 1 });

// Create indexes for events collection
db.events.createIndex({ "business_id": 1, "user_id": 1 });
db.events.createIndex({ "business_id": 1, "timestamp": -1 });
db.events.createIndex({ "global_uid": 1 });
db.events.createIndex({ "session_id": 1 });

// Create indexes for users collection
db.users.createIndex({ "business_id": 1, "user_id": 1 }, { unique: true });

// Create indexes for variants collection
db.variants.createIndex({ "business_id": 1, "user_id": 1 });
db.variants.createIndex({ "business_id": 1, "variant_id": 1 });

// Create indexes for data sharing agreements
db.data_sharing_agreements.createIndex({ "agreement_id": 1 }, { unique: true });
db.data_sharing_agreements.createIndex({ "from_business_id": 1, "status": 1 });
db.data_sharing_agreements.createIndex({ "to_business_id": 1, "status": 1 });

// Create demo businesses for testing cross-site tracking
db.businesses.insertMany([
    {
        "business_id": "biz_demo",
        "name": "Demo Store",
        "domain": "localhost",
        "allowed_domains": ["localhost", "127.0.0.1"],
        "api_key": "pk_demo_test123",
        "api_secret_hash": "demo_secret_hash",
        "tier": "growth",
        "sharing_level": "aggregate",
        "partner_ids": ["biz_shoes", "biz_clothes"],
        "created_at": new Date(),
        "updated_at": new Date(),
        "is_active": true,
        "monthly_event_limit": 1000000,
        "monthly_events_used": 0
    },
    {
        "business_id": "biz_shoes",
        "name": "ShoeMax (Business A)",
        "domain": "localhost",
        "allowed_domains": ["localhost", "127.0.0.1"],
        "api_key": "pk_demo_shoes_123",
        "api_secret_hash": "shoes_secret_hash",
        "tier": "growth",
        "sharing_level": "aggregate",
        "partner_ids": ["biz_clothes", "biz_demo"],
        "created_at": new Date(),
        "updated_at": new Date(),
        "is_active": true,
        "monthly_event_limit": 1000000,
        "monthly_events_used": 0
    },
    {
        "business_id": "biz_clothes",
        "name": "StyleHub (Business B)",
        "domain": "localhost",
        "allowed_domains": ["localhost", "127.0.0.1"],
        "api_key": "pk_demo_clothes_456",
        "api_secret_hash": "clothes_secret_hash",
        "tier": "growth",
        "sharing_level": "aggregate",
        "partner_ids": ["biz_shoes", "biz_demo"],
        "created_at": new Date(),
        "updated_at": new Date(),
        "is_active": true,
        "monthly_event_limit": 1000000,
        "monthly_events_used": 0
    }
]);

// Create pre-approved data sharing agreements between demo businesses
db.data_sharing_agreements.insertMany([
    {
        "agreement_id": "agr_shoes_clothes",
        "from_business_id": "biz_shoes",
        "to_business_id": "biz_clothes",
        "sharing_level": "aggregate",
        "permissions": {
            "share_behavioral_vectors": true,
            "share_identity_states": true,
            "share_conversion_data": false,
            "share_raw_events": false
        },
        "status": "active",
        "initiated_at": new Date(),
        "accepted_at": new Date()
    },
    {
        "agreement_id": "agr_clothes_shoes",
        "from_business_id": "biz_clothes",
        "to_business_id": "biz_shoes",
        "sharing_level": "aggregate",
        "permissions": {
            "share_behavioral_vectors": true,
            "share_identity_states": true,
            "share_conversion_data": false,
            "share_raw_events": false
        },
        "status": "active",
        "initiated_at": new Date(),
        "accepted_at": new Date()
    }
]);

print('MongoDB initialized with indexes, demo businesses, and data sharing agreements');
