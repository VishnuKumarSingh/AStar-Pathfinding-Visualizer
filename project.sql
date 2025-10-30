-- Create Database
CREATE DATABASE IF NOT EXISTS smart_library;
USE smart_library;

-- Drop tables if they exist (for re-running the script)
DROP TABLE IF EXISTS overdue_log;
DROP TABLE IF EXISTS borrowings;
DROP TABLE IF EXISTS books;
DROP TABLE IF EXISTS users;

-- Users Table
CREATE TABLE users (
    user_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    phone VARCHAR(15),
    role ENUM('student', 'staff') DEFAULT 'student',
    join_date DATE DEFAULT (CURRENT_DATE)
);

-- Books Table
CREATE TABLE books (
    book_id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(200) NOT NULL,
    author VARCHAR(100) NOT NULL,
    category VARCHAR(50),
    isbn VARCHAR(20) UNIQUE,
    total_copies INT DEFAULT 1 CHECK (total_copies > 0),
    available_copies INT DEFAULT 1 CHECK (available_copies >= 0),
    publish_year YEAR,
    price DECIMAL(10,2) CHECK (price > 0)
);

-- Borrowings Table
CREATE TABLE borrowings (
    borrow_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    book_id INT,
    borrow_date DATE DEFAULT (CURRENT_DATE),
    due_date DATE NOT NULL,
    return_date DATE NULL,
    fine DECIMAL(10,2) DEFAULT 0 CHECK (fine >= 0),
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    FOREIGN KEY (book_id) REFERENCES books(book_id) ON DELETE CASCADE
);

-- Overdue Log Table
CREATE TABLE overdue_log (
    log_id INT AUTO_INCREMENT PRIMARY KEY,
    borrow_id INT,
    user_id INT,
    book_id INT,
    days_overdue INT,
    fine_amount DECIMAL(10,2),
    log_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (borrow_id) REFERENCES borrowings(borrow_id),
    FOREIGN KEY (user_id) REFERENCES users(user_id),
    FOREIGN KEY (book_id) REFERENCES books(book_id)
);

-- Trigger for Overdue Notifications
DELIMITER //
CREATE TRIGGER check_overdue
BEFORE UPDATE ON borrowings
FOR EACH ROW
BEGIN
    IF NEW.return_date IS NOT NULL AND NEW.return_date > OLD.due_date THEN
        SET NEW.fine = (DATEDIFF(NEW.return_date, OLD.due_date)) * 1.00; -- ₹1 per day fine
        INSERT INTO overdue_log (borrow_id, user_id, book_id, days_overdue, fine_amount)
        VALUES (OLD.borrow_id, OLD.user_id, OLD.book_id, DATEDIFF(NEW.return_date, OLD.due_date), NEW.fine);
    END IF;
END;
//
DELIMITER ;

-- Trigger to Update Available Copies on Borrow
DELIMITER //
CREATE TRIGGER update_available_on_borrow
AFTER INSERT ON borrowings
FOR EACH ROW
BEGIN
    UPDATE books
    SET available_copies = available_copies - 1
    WHERE book_id = NEW.book_id;
END;
//
DELIMITER ;

-- Trigger to Update Available Copies on Return
DELIMITER //
CREATE TRIGGER update_available_on_return
AFTER UPDATE ON borrowings
FOR EACH ROW
BEGIN
    IF NEW.return_date IS NOT NULL AND OLD.return_date IS NULL THEN
        UPDATE books
        SET available_copies = available_copies + 1
        WHERE book_id = NEW.book_id;
    END IF;
END;
//
DELIMITER ;

-- Stored Procedure for Book Recommendations
DELIMITER //
CREATE PROCEDURE get_recommendations(IN user_id_param INT)
BEGIN
    DECLARE borrowed_books TEXT DEFAULT '';
    DECLARE similar_users TEXT DEFAULT '';

    -- Get books borrowed by this user
    SELECT GROUP_CONCAT(book_id) INTO borrowed_books
    FROM borrowings WHERE user_id = user_id_param;

    IF borrowed_books IS NOT NULL THEN
        -- Find users who borrowed similar books
        SET @query = CONCAT('SELECT GROUP_CONCAT(DISTINCT user_id) INTO @similar_users FROM borrowings WHERE book_id IN (', borrowed_books, ') AND user_id != ', user_id_param);
        PREPARE stmt FROM @query;
        EXECUTE stmt;
        DEALLOCATE PREPARE stmt;

        IF @similar_users IS NOT NULL THEN
            -- Recommend other books borrowed by similar users
            SET @rec_query = CONCAT('SELECT b.title, COUNT(br.borrow_id) AS freq
                                     FROM borrowings br
                                     JOIN books b ON br.book_id = b.book_id
                                     WHERE br.user_id IN (', @similar_users, ')
                                     AND br.book_id NOT IN (', borrowed_books, ')
                                     GROUP BY br.book_id
                                     ORDER BY freq DESC
                                     LIMIT 3');
            PREPARE stmt FROM @rec_query;
            EXECUTE stmt;
            DEALLOCATE PREPARE stmt;
        ELSE
            SELECT 'No recommendations available' AS message;
        END IF;
    ELSE
        SELECT 'User has no borrowing history' AS message;
    END IF;
END;
//
DELIMITER ;

-- Views for Analytics
CREATE OR REPLACE VIEW top_borrowed_books AS
SELECT b.title, COUNT(br.borrow_id) AS borrow_count
FROM borrowings br
JOIN books b ON br.book_id = b.book_id
GROUP BY b.book_id
ORDER BY borrow_count DESC
LIMIT 5;

CREATE OR REPLACE VIEW user_activity AS
SELECT u.name, COUNT(br.borrow_id) AS borrow_count
FROM borrowings br
JOIN users u ON br.user_id = u.user_id
GROUP BY u.user_id
ORDER BY borrow_count DESC;

CREATE OR REPLACE VIEW total_revenue AS
SELECT IFNULL(SUM(fine), 0) AS total_fine_revenue
FROM borrowings
WHERE fine > 0;

-- Sample Data
INSERT INTO users (name, email, phone, role) VALUES
('Alice Johnson', 'alice@example.com', '1234567890', 'student'),
('Bob Smith', 'bob@example.com', '0987654321', 'staff'),
('Charlie Brown', 'charlie@example.com', '1122334455', 'student');

INSERT INTO books (title, author, category, isbn, total_copies, available_copies, publish_year, price) VALUES
('Python Programming', 'John Doe', 'Programming', '1234567890', 5, 5, 2020, 29.99),
('Data Structures', 'Jane Smith', 'Computer Science', '0987654321', 3, 3, 2019, 39.99),
('Database Systems', 'Mike Johnson', 'Database', '1122334455', 4, 4, 2021, 49.99),
('Algorithms', 'Sara Lee', 'Computer Science', '5566778899', 2, 2, 2018, 34.99);

-- Borrow some books
INSERT INTO borrowings (user_id, book_id, due_date) VALUES
(1, 1, '2023-12-01'),
(2, 2, '2023-11-25'),
(3, 3, '2023-11-30');

-- Simulate an overdue return
UPDATE borrowings SET return_date = '2023-12-05' WHERE borrow_id = 1;

SELECT * FROM total_revenue;
