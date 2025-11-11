# Hough Transform Analysis - OOP Architecture

## Overview

This document describes the refactored Object-Oriented Programming (OOP) architecture of the Hough Transform Analysis system. The refactoring applies enterprise-level design patterns and follows SOLID principles for maximum maintainability, testability, and extensibility.

## Table of Contents

1. [Architectural Overview](#architectural-overview)
2. [Design Patterns Used](#design-patterns-used)
3. [SOLID Principles](#solid-principles)
4. [Directory Structure](#directory-structure)
5. [Core Components](#core-components)
6. [Usage Examples](#usage-examples)
7. [Benefits of Refactoring](#benefits-of-refactoring)

---

## Architectural Overview

The system follows a **layered architecture** with clear separation of concerns:

```
┌──────────────────────────────────────────────────────┐
│                   Main Application                    │
│                  (main_refactored.py)                 │
└───────────────────────┬──────────────────────────────┘
                        │
                        ▼
┌──────────────────────────────────────────────────────┐
│                  Facade Layer                         │
│              (HoughAnalysisFacade)                    │
│         Simplified high-level API                     │
└──────────┬───────────────────────────────────────────┘
           │
           ├─────────────────┬──────────────────┬───────┐
           ▼                 ▼                  ▼       ▼
    ┌──────────┐      ┌──────────┐      ┌──────────┐ ┌──────────┐
    │ Services │      │Repository│      │  Utils   │ │ Strategy │
    │  Layer   │      │  Layer   │      │  Layer   │ │  Layer   │
    └──────────┘      └──────────┘      └──────────┘ └──────────┘
           │                 │
           └────────┬────────┘
                    ▼
           ┌─────────────────┐
           │  Domain Models  │
           │  (Entities &    │
           │ Value Objects)  │
           └─────────────────┘
```

### Layer Responsibilities

1. **Domain Layer**: Core business entities and value objects
2. **Strategy Layer**: Interchangeable algorithms (easing functions)
3. **Repository Layer**: Data access abstraction
4. **Service Layer**: Business logic and orchestration
5. **Facade Layer**: Simplified API for complex subsystems
6. **Utils Layer**: Cross-cutting concerns (observers, helpers)

---

## Design Patterns Used

### 1. **Facade Pattern**
- **Class**: `HoughAnalysisFacade`
- **Purpose**: Provides a simplified interface to the complex subsystem
- **Benefits**: Reduces coupling, simplifies client code

```python
# Complex subsystem hidden behind simple API
facade = HoughAnalysisFacade.create_with_default_config()
stats = facade.run_complete_analysis()  # One line!
```

### 2. **Repository Pattern**
- **Classes**: `ParticleRepository`, `HoughRepository`, `TrainingDataRepository`
- **Purpose**: Abstracts data access logic
- **Benefits**: Separation of concerns, easier testing, swappable data sources

```python
particle_repo = ParticleRepository(data_path)
tracks = particle_repo.get_tracks_for_event(event_id)
```

### 3. **Strategy Pattern**
- **Classes**: `EasingStrategy` and implementations
- **Purpose**: Interchangeable algorithms for easing functions
- **Benefits**: Open/Closed Principle, easy to add new strategies

```python
# Can switch strategies without changing client code
strategy = EasingStrategyFactory.create("InSquare")
slicer = TrackSlicerService(strategy, config)
```

### 4. **Builder Pattern**
- **Class**: `AnalysisConfigBuilder`
- **Purpose**: Construct complex configuration objects step by step
- **Benefits**: Flexible object creation, fluent interface

```python
config = (AnalysisConfigBuilder()
          .with_hough_config(nbin_phi=7000, nbin_qpt=216)
          .with_peak_detection_config(threshold_abs=5.0)
          .with_easing_type("InSquare")
          .build())
```

### 5. **Observer Pattern**
- **Classes**: `ProgressObserver`, `ConsoleProgressObserver`
- **Purpose**: Notify observers of progress events
- **Benefits**: Loose coupling, extensible notification system

```python
observer = ConsoleProgressObserver(verbose=True)
facade = HoughAnalysisFacade(config, observer)
```

### 6. **Singleton Pattern**
- **Class**: `ParticleChargeRegistry`
- **Purpose**: Ensure single global instance of charge registry
- **Benefits**: Controlled access to shared resource

### 7. **Factory Pattern**
- **Class**: `EasingStrategyFactory`
- **Purpose**: Create strategy instances by name
- **Benefits**: Centralized object creation, easy registration of new strategies

### 8. **Value Object Pattern**
- **Classes**: `Peak`, `Particle`, `HoughSquare`
- **Purpose**: Immutable objects representing concepts
- **Benefits**: Thread-safety, clarity of intent

---

## SOLID Principles

### Single Responsibility Principle (SRP)
Each class has one reason to change:
- `PeakDetectorService`: Only peak detection logic
- `TrackSlicerService`: Only track slicing logic
- `ParticleRepository`: Only particle data access

### Open/Closed Principle (OCP)
Open for extension, closed for modification:
- New easing strategies can be added without modifying existing code
- Custom observers can be created by implementing `ProgressObserver`

### Liskov Substitution Principle (LSP)
Subtypes are substitutable for their base types:
- Any `EasingStrategy` can replace another
- Any `ProgressObserver` can replace another

### Interface Segregation Principle (ISP)
Clients aren't forced to depend on interfaces they don't use:
- Small, focused interfaces like `EasingStrategy`
- Specific observer methods for different events

### Dependency Inversion Principle (DIP)
Depend on abstractions, not concretions:
- Services depend on abstract `EasingStrategy`, not concrete implementations
- Facade depends on service interfaces, not implementations

---

## Directory Structure

```
hough/
├── domain/                    # Domain models (entities & value objects)
│   ├── __init__.py
│   ├── particle.py           # Particle, ParticleChargeRegistry
│   ├── peak.py               # Peak, PeakCollection
│   ├── track.py              # Track, TrackCollection
│   └── hough_square.py       # HoughSquare, SquareClassification
│
├── config/                    # Configuration management
│   ├── __init__.py
│   └── analysis_config.py    # AnalysisConfig, Builder
│
├── strategies/                # Strategy pattern implementations
│   ├── __init__.py
│   └── easing_strategy.py    # EasingStrategy, implementations, Factory
│
├── repositories/              # Data access layer
│   ├── __init__.py
│   ├── particle_repository.py       # Particle data access
│   ├── hough_repository.py          # Hough data access
│   └── training_data_repository.py  # Training data persistence
│
├── services/                  # Business logic layer
│   ├── __init__.py
│   ├── peak_detector.py      # Peak detection service
│   ├── track_slicer.py       # Track slicing service
│   ├── hough_matcher.py      # Peak-track matching service
│   └── visualizer.py         # Visualization service
│
├── facades/                   # Facade pattern
│   ├── __init__.py
│   └── analysis_facade.py    # High-level API facade
│
├── utils/                     # Utilities and cross-cutting concerns
│   ├── __init__.py
│   └── observers.py          # Observer pattern for progress
│
├── main_refactored.py        # New OOP entry point
├── main.py                   # Legacy procedural entry point
└── OOP_ARCHITECTURE.md       # This file
```

---

## Core Components

### Domain Layer

#### **Particle**
```python
@dataclass(frozen=True)
class Particle:
    """Immutable value object for particles"""
    pdg_id: int
    charge: float
    pt: float
    # ... other fields
```

#### **Peak**
```python
@dataclass(frozen=True)
class Peak:
    """Immutable value object for peaks"""
    x: float
    y: float
    height: float

    def distance_to(self, other: Peak) -> float:
        """Calculate distance to another peak"""
```

#### **Track**
```python
@dataclass
class Track:
    """Entity representing a track"""
    event_id: int
    phi_bin: float
    # ... other fields

    def mark_reconstructed(self) -> None:
        """Business logic method"""
```

### Service Layer

#### **PeakDetectorService**
```python
class PeakDetectorService:
    """Encapsulates peak detection logic"""

    def find_peaks(self, histogram) -> PeakCollection:
        """Find peaks in histogram"""
```

#### **TrackSlicerService**
```python
class TrackSlicerService:
    """Handles track slicing with strategies"""

    def filter_tracks_for_slice(
        self, tracks: TrackCollection, slice_num: int
    ) -> TrackCollection:
        """Filter tracks by slice criteria"""
```

#### **HoughMatcherService**
```python
class HoughMatcherService:
    """Matches peaks with tracks"""

    def match_and_extract_squares(
        self, values, peaks, tracks
    ) -> Tuple[HoughSquareCollection, np.ndarray]:
        """Match peaks and extract training squares"""
```

### Repository Layer

#### **ParticleRepository**
```python
class ParticleRepository:
    """Repository for particle data access"""

    def load_particles(self) -> pd.DataFrame:
        """Load particles from ROOT files"""

    def get_tracks_for_event(self, event_id) -> TrackCollection:
        """Get tracks for specific event"""
```

---

## Usage Examples

### Basic Usage (Facade Pattern)

```python
from facades.analysis_facade import HoughAnalysisFacade

# Simplest possible usage
facade = HoughAnalysisFacade.create_with_default_config()
stats = facade.run_complete_analysis()

print(f"Efficiency: {stats.reconstruction_efficiency:.2%}")
```

### Custom Configuration (Builder Pattern)

```python
from config.analysis_config import AnalysisConfigBuilder

config = (AnalysisConfigBuilder()
          .with_hough_config(
              nbin_phi=7000,
              nbin_qpt=216,
              square_size=16
          )
          .with_peak_detection_config(
              threshold_abs=5.0,
              min_distance=2
          )
          .with_processing_config(
              slice_list=[-1],
              num_files=8
          )
          .with_easing_type("InSquare")
          .build())

facade = HoughAnalysisFacade(config)
facade.run_complete_analysis()
```

### Custom Observer (Observer Pattern)

```python
from utils.observers import ProgressObserver

class CustomObserver(ProgressObserver):
    def on_slice_complete(self, event_id, slice_num, peaks, tracks, matched):
        # Custom logging or metrics
        send_to_monitoring_system(peaks, matched)

observer = CustomObserver()
facade = HoughAnalysisFacade(config, observer)
facade.run_complete_analysis()
```

### Adding New Easing Strategy (Strategy Pattern)

```python
from strategies.easing_strategy import EasingStrategy, EasingStrategyFactory

class CustomEasing(EasingStrategy):
    def ease(self, x: float) -> float:
        return x ** 2  # Custom algorithm

    def name(self) -> str:
        return "Custom"

# Register new strategy
EasingStrategyFactory.register_strategy("Custom", CustomEasing)

# Use it
config = (AnalysisConfigBuilder()
          .with_easing_type("Custom")
          .build())
```

---

## Benefits of Refactoring

### 1. **Maintainability**
- Clear separation of concerns
- Each class has single responsibility
- Easy to locate and fix bugs

### 2. **Testability**
- Dependencies can be mocked
- Each component tested in isolation
- Repository pattern allows test doubles

### 3. **Extensibility**
- New features added without modifying existing code
- Strategy pattern allows new algorithms
- Observer pattern allows new monitoring

### 4. **Reusability**
- Services can be used independently
- Domain models reusable across contexts
- Repositories can be reused for different analyses

### 5. **Readability**
- Self-documenting code structure
- Clear naming conventions
- Logical organization

### 6. **Flexibility**
- Configuration easily customized
- Algorithms easily swapped
- Data sources easily changed

### 7. **Performance**
- Repository caching
- Lazy loading where appropriate
- Efficient memory management

---

## Comparison: Before vs After

### Before (Procedural)
```python
# main.py - 200+ lines of procedural code
# Everything mixed together
truetracks = {}
true_squares = []
false_squares = []
n_truetracks = 0
event_list = []

for file in root_files:
    # Nested loops, global state, tight coupling
    for key in f.keys():
        # Processing logic mixed with I/O
        # Hard to test, hard to modify
```

### After (OOP)
```python
# main_refactored.py - Clean and simple
facade = HoughAnalysisFacade.create_with_default_config()
stats = facade.run_complete_analysis()
# Done! All complexity hidden in well-organized classes
```

---

## Design Pattern Summary

| Pattern | Classes | Purpose |
|---------|---------|---------|
| **Facade** | `HoughAnalysisFacade` | Simplified API |
| **Repository** | `*Repository` | Data access abstraction |
| **Strategy** | `EasingStrategy` | Interchangeable algorithms |
| **Builder** | `AnalysisConfigBuilder` | Flexible object construction |
| **Observer** | `ProgressObserver` | Event notification |
| **Singleton** | `ParticleChargeRegistry` | Single instance |
| **Factory** | `EasingStrategyFactory` | Object creation |
| **Value Object** | `Peak`, `Particle`, etc. | Immutable concepts |

---

## Conclusion

This refactoring transforms a procedural codebase into a well-architected OOP system that:

✅ Follows SOLID principles
✅ Uses appropriate design patterns
✅ Has clear separation of concerns
✅ Is easily testable and maintainable
✅ Is extensible for future requirements
✅ Has a simple, clean API

The investment in proper architecture pays dividends in code quality, team productivity, and long-term maintainability.
