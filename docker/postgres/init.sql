CREATE EXTENSION IF NOT EXISTS vector;
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ===== ENUMS =====
CREATE TYPE order_status AS ENUM ('pending', 'processing', 'shipped', 'delivered', 'cancelled', 'returned');
CREATE TYPE invoice_status AS ENUM ('draft', 'sent', 'paid', 'overdue', 'cancelled');
CREATE TYPE tracking_status AS ENUM ('order_placed', 'processing', 'shipped', 'in_transit', 'delivered', 'exception');
CREATE TYPE support_ticket_status AS ENUM ('open', 'in_progress', 'waiting_customer', 'resolved', 'closed','reopen');

-- ===== CUSTOMER TABLE =====
CREATE TABLE customer (
    customer_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) NOT NULL UNIQUE CHECK (email ~* '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}$'),
    password VARCHAR(255) NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT customer_name_length CHECK (length(name) > 0)
);

-- ===== ADDRESS TABLE =====
CREATE TABLE address (
    address_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    customer_id UUID NOT NULL,
    full_name VARCHAR(100) NOT NULL,
    phone VARCHAR(15) NOT NULL,
    address_line1 VARCHAR(255) NOT NULL,
    address_line2 VARCHAR(255),
    city VARCHAR(100) NOT NULL,
    state VARCHAR(100) NOT NULL,
    postal_code VARCHAR(10) NOT NULL,
    country VARCHAR(100) NOT NULL DEFAULT 'India',
    is_default BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (customer_id) REFERENCES customer(customer_id) ON DELETE CASCADE,
    CONSTRAINT address_full_name_length CHECK (length(full_name) > 0),
    CONSTRAINT address_phone_length CHECK (length(phone) > 0),
    CONSTRAINT address_line1_length CHECK (length(address_line1) > 0)
);

-- ===== INVOICE TABLE =====
CREATE TABLE invoice (
    invoice_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    customer_id UUID NOT NULL,
    invoice_number VARCHAR(255) NOT NULL UNIQUE,
    status invoice_status NOT NULL DEFAULT 'draft',
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (customer_id) REFERENCES customer(customer_id) ON DELETE CASCADE,
    CONSTRAINT invoice_number_length CHECK (length(invoice_number) > 0)
);

-- ===== ORDERS TABLE =====
CREATE TABLE orders (
    order_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    customer_id UUID NOT NULL,
    invoice_id UUID NOT NULL,
    address_id UUID NOT NULL,
    status order_status NOT NULL DEFAULT 'pending',
    estimated_delivery_date DATE,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (customer_id) REFERENCES customer(customer_id) ON DELETE CASCADE,
    FOREIGN KEY (invoice_id) REFERENCES invoice(invoice_id) ON DELETE CASCADE,
    FOREIGN KEY (address_id) REFERENCES address(address_id),
    CONSTRAINT delivery_date_future CHECK (estimated_delivery_date IS NULL OR estimated_delivery_date > created_at::date)
);

-- ===== PRODUCT TABLE =====
CREATE TABLE product (
    product_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    category VARCHAR(255) NOT NULL,
    sub_category VARCHAR(255),
    name VARCHAR(255) NOT NULL,
    image_url TEXT,
    rating NUMERIC(2,1) NOT NULL DEFAULT 0,
    total_rating INT NOT NULL DEFAULT 0,
    price NUMERIC(12,2) NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT product_category_length CHECK (length(category) > 0),
    CONSTRAINT product_name_length CHECK (length(name) > 0),
    CONSTRAINT product_rating_range CHECK (rating >= 0 AND rating <= 5),
    CONSTRAINT product_total_rating_non_negative CHECK (total_rating >= 0),
    CONSTRAINT product_price_non_negative CHECK (price >= 0)
);

-- ===== PRODUCT_ITEM TABLE =====
CREATE TABLE product_item (
    product_item_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    order_id UUID NOT NULL,
    product_id UUID NOT NULL,
    quantity INT NOT NULL,
    returnable BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (order_id) REFERENCES orders(order_id) ON DELETE CASCADE,
    FOREIGN KEY (product_id) REFERENCES product(product_id),
    CONSTRAINT quantity_positive CHECK (quantity > 0)
);

-- ===== TRACKING_EVENT TABLE =====
CREATE TABLE tracking_event (
    tracking_event_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    order_id UUID NOT NULL,
    status tracking_status NOT NULL,
    location VARCHAR(255),
    timestamp TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (order_id) REFERENCES orders(order_id) ON DELETE CASCADE
);

-- ===== DOCUMENT TABLE (Vector DB) =====
CREATE TABLE document (
    document_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    original_text TEXT,
    embedding_vector vector(3072),
    metadata JSONB,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- ===== CONVERSATION TABLE =====
CREATE TABLE conversation (
    conversation_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    customer_id UUID NOT NULL,
    title VARCHAR(255),
    messages JSONB DEFAULT '[]'::jsonb,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (customer_id) REFERENCES customer(customer_id) ON DELETE CASCADE,
    CONSTRAINT conversation_title_length CHECK (title IS NULL OR length(title) > 0)
);

-- ===== SUPPORT_TICKET TABLE =====
CREATE TABLE support_ticket (
    support_ticket_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    order_id UUID NOT NULL,
    conversation_id UUID,
    summary TEXT NOT NULL,
    status support_ticket_status NOT NULL DEFAULT 'open',
    human_response TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (order_id) REFERENCES orders(order_id) ON DELETE CASCADE,
    FOREIGN KEY (conversation_id) REFERENCES conversation(conversation_id) ON DELETE SET NULL,
    CONSTRAINT summary_length CHECK (length(summary) > 0)
);

-- ===== INDEXES FOR PERFORMANCE =====
CREATE INDEX idx_customer_email ON customer(email);
CREATE INDEX idx_address_customer_id ON address(customer_id);
CREATE INDEX idx_address_postal_code ON address(postal_code);
CREATE UNIQUE INDEX idx_address_one_default_per_customer ON address(customer_id) WHERE is_default = TRUE;
CREATE INDEX idx_invoice_number ON invoice(invoice_number);
CREATE INDEX idx_invoice_status ON invoice(status);
CREATE INDEX idx_orders_customer_id ON orders(customer_id);
CREATE INDEX idx_orders_invoice_id ON orders(invoice_id);
CREATE INDEX idx_orders_address_id ON orders(address_id);
CREATE INDEX idx_orders_status ON orders(status);
CREATE INDEX idx_orders_created_at ON orders(created_at);
CREATE INDEX idx_product_category ON product(category);
CREATE INDEX idx_product_sub_category ON product(sub_category);
CREATE INDEX idx_product_category_sub_category ON product(category, sub_category);
CREATE INDEX idx_product_name ON product(name);
CREATE INDEX idx_product_price ON product(price);
CREATE INDEX idx_product_rating ON product(rating);
CREATE INDEX idx_product_item_order_id ON product_item(order_id);
CREATE INDEX idx_product_item_product_id ON product_item(product_id);
CREATE INDEX idx_tracking_event_order_id ON tracking_event(order_id);
CREATE INDEX idx_tracking_event_status ON tracking_event(status);
CREATE INDEX idx_tracking_event_timestamp ON tracking_event(timestamp);
CREATE INDEX idx_document_metadata ON document USING GIN(metadata);
CREATE INDEX idx_document_embedding ON document USING ivfflat(embedding_vector vector_cosine_ops);
CREATE INDEX idx_conversation_customer_id ON conversation(customer_id);
CREATE INDEX idx_support_ticket_order_id ON support_ticket(order_id);
CREATE INDEX idx_support_ticket_conversation_id ON support_ticket(conversation_id);
CREATE INDEX idx_support_ticket_status ON support_ticket(status);

-- ===== TRIGGERS FOR UPDATED_AT =====
CREATE OR REPLACE FUNCTION update_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_orders_updated_at
BEFORE UPDATE ON orders
FOR EACH ROW
EXECUTE FUNCTION update_timestamp();

CREATE TRIGGER trigger_address_updated_at
BEFORE UPDATE ON address
FOR EACH ROW
EXECUTE FUNCTION update_timestamp();

CREATE TRIGGER trigger_product_updated_at
BEFORE UPDATE ON product
FOR EACH ROW
EXECUTE FUNCTION update_timestamp();

CREATE TRIGGER trigger_conversation_updated_at
BEFORE UPDATE ON conversation
FOR EACH ROW
EXECUTE FUNCTION update_timestamp();

CREATE TRIGGER trigger_support_ticket_updated_at
BEFORE UPDATE ON support_ticket
FOR EACH ROW
EXECUTE FUNCTION update_timestamp();

-- ===== TABLE COMMENTS =====
COMMENT ON TABLE customer IS 'Stores customer account information';
COMMENT ON TABLE address IS 'Stores customer shipping addresses';
COMMENT ON TABLE invoice IS 'Stores invoice records';
COMMENT ON TABLE orders IS 'Stores customer orders';
COMMENT ON TABLE product IS 'Stores product catalog details';
COMMENT ON TABLE product_item IS 'Stores individual products in orders';
COMMENT ON TABLE tracking_event IS 'Stores order tracking events';
COMMENT ON TABLE document IS 'Vector database for documents with embeddings';
COMMENT ON TABLE conversation IS 'Stores conversations and chat messages';
COMMENT ON TABLE support_ticket IS 'Stores customer support tickets';