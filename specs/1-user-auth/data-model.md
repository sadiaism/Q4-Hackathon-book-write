# Data Model: User Authentication and Onboarding

## User Entity
**Description**: Represents a registered user with authentication credentials

**Fields**:
- id: String (Primary Key, auto-generated)
- email: String (Unique, required)
- name: String (Optional)
- emailVerified: DateTime (Optional, tracks email verification)
- createdAt: DateTime (Auto-generated)
- updatedAt: DateTime (Auto-generated)

**Relationships**:
- UserProfile (one-to-one): User has one profile with background information

## UserProfile Entity
**Description**: Contains user's software and hardware background information linked to a user account

**Fields**:
- id: String (Primary Key, auto-generated)
- userId: String (Foreign Key, required, references User.id)
- programmingLevel: String (Enum: "beginner", "intermediate", "advanced", "expert")
- languages: String[] (Array of programming languages)
- tools: String[] (Array of tools used)
- ram: String (Laptop RAM, e.g. "8GB", "16GB", "32GB")
- processor: String (Laptop processor, e.g. "Intel i5", "AMD Ryzen 7")
- gpu: String (Laptop GPU, e.g. "Integrated", "RTX 3060")
- learningGoal: String (Text field for user's learning goal)
- completed: Boolean (Flag to track if onboarding is complete, default: false)
- createdAt: DateTime (Auto-generated)
- updatedAt: DateTime (Auto-generated)

**Validation Rules**:
- userId must reference an existing User
- programmingLevel must be one of the defined enum values
- languages and tools arrays should have reasonable length limits
- ram, processor, gpu fields should be validated for expected formats
- learningGoal should have reasonable character limits (e.g., max 500 characters)

**State Transitions**:
- Profile starts as incomplete (completed: false) after signup
- Profile becomes complete (completed: true) after onboarding form submission
- Profile can be updated after completion to modify background information