# Project Roadmap

This project will be developed incrementally, starting with a minimal proof of concept and gradually evolving into a complete Windows application. Each milestone introduces new features while keeping the project functional and easy to test.

---

## Phase 1 — Time Monitoring Prototype

**Goal:** Verify that the application can detect a specific time.

### Features

* Monitor the system clock.
* Check the current time periodically.
* Trigger an action when a predefined time is reached.

### Deliverable

A console application that prints a reminder message when the scheduled time is detected.

---

## Phase 2 — Sound Notifications

**Goal:** Turn the prototype into a functional reminder.

### Features

* Play an alert sound when a reminder is triggered.
* Support Windows sound playback.

### Deliverable

A console application that displays a reminder and plays a notification sound.

---

## Phase 3 — Basic Graphical Interface

**Goal:** Replace console messages with a user-friendly interface.

### Features

* Create a simple window using Tkinter.
* Display reminder notifications.
* Add a confirmation button.

### Deliverable

A graphical pop-up window that appears when a reminder is triggered.

---

## Phase 4 — Configurable Reminder Times

**Goal:** Allow reminder schedules to be modified without editing source code.

### Features

* Store reminder times in a configuration file.
* Load settings automatically on s
