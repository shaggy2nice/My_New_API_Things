package main

import (
	"bufio"
	"encoding/json"
	"fmt"
	"os"
	"strconv"
	"strings"
	"time"
)

// Constants for status and priority
const (
	StatusInProgress = "in progress"
	StatusOnHold     = "on hold"
	StatusComplete   = "complete"

	PriorityHigh   = "high"
	PriorityMedium = "medium"
	PriorityLow    = "low"
)

type Task struct {
	Description string    `json:"description"`
	DueDate     time.Time `json:"due_date"`
	Priority    string    `json:"priority"`
	Status      string    `json:"status"`
}

// Custom JSON marshaling for Task
func (t Task) MarshalJSON() ([]byte, error) {
	type Alias Task
	return json.Marshal(&struct {
		DueDate string `json:"due_date"`
		Alias
	}{
		DueDate: t.DueDate.Format("2006-01-02"),
		Alias:   Alias(t),
	})
}

// Custom JSON unmarshaling for Task
func (t *Task) UnmarshalJSON(data []byte) error {
	type Alias Task
	aux := &struct {
		DueDate string `json:"due_date"`
		*Alias
	}{
		Alias: (*Alias)(t),
	}
	if err := json.Unmarshal(data, &aux); err != nil {
		return err
	}
	if aux.DueDate != "" {
		parsedTime, err := time.Parse("2006-01-02", aux.DueDate)
		if err != nil {
			return err
		}
		t.DueDate = parsedTime
	}
	return nil
}

func (t *Task) IsOverdue() bool {
	return !t.DueDate.IsZero() && time.Now().After(t.DueDate)
}

func (t *Task) DueWithinOneDay() bool {
	return !t.DueDate.IsZero() && time.Until(t.DueDate) <= 24*time.Hour
}

func (t *Task) String() string {
	return fmt.Sprintf("%s (Due: %s, Priority: %s, Status: %s)",
		t.Description, t.FormatDueDate(), t.Priority, t.Status)
}

func (t *Task) FormatDueDate() string {
	if t.DueDate.IsZero() {
		return "No due date"
	}
	now := time.Now()
	switch {
	case t.DueDate.Year() == now.Year() && t.DueDate.YearDay() == now.YearDay():
		return "Today"
	case t.DueDate.Year() == now.Year() && t.DueDate.YearDay() == now.YearDay()+1:
		return "Tomorrow"
	default:
		return t.DueDate.Format("2006-01-02")
	}
}

func ParseDueDate(dueDate string) (time.Time, error) {
	now := time.Now()
	switch strings.ToLower(dueDate) {
	case "today":
		return now, nil
	case "tomorrow":
		return now.AddDate(0, 0, 1), nil
	case "next week":
		return now.AddDate(0, 0, 7), nil
	case "next month":
		return now.AddDate(0, 1, 0), nil
	default:
		return time.Parse("2006-01-02", dueDate)
	}
}

func getTaskFromUser(scanner *bufio.Scanner) (*Task, error) {
	fmt.Print("Enter the task description: ")
	scanner.Scan()
	description := strings.TrimSpace(scanner.Text())

	var dueDate time.Time
	for {
		fmt.Print("Enter the due date (YYYY-MM-DD, today, tomorrow, next week, next month) or leave blank for no due date: ")
		scanner.Scan()
		dueDateStr := strings.TrimSpace(scanner.Text())
		if dueDateStr == "" {
			break
		}
		var err error
		dueDate, err = ParseDueDate(dueDateStr)
		if err == nil {
			break
		}
		fmt.Println("Invalid date format. Please try again.")
	}

	fmt.Printf("Enter priority (%s/%s/%s): ", PriorityHigh, PriorityMedium, PriorityLow)
	scanner.Scan()
	priority := strings.ToLower(strings.TrimSpace(scanner.Text()))
	if priority != PriorityHigh && priority != PriorityLow {
		priority = PriorityMedium
	}

	fmt.Printf("Enter status (%s, %s, %s): ", StatusInProgress, StatusOnHold, StatusComplete)
	scanner.Scan()
	status := strings.ToLower(strings.TrimSpace(scanner.Text()))
	if status != StatusOnHold && status != StatusComplete {
		status = StatusInProgress
	}

	return &Task{
		Description: description,
		DueDate:     dueDate,
		Priority:    priority,
		Status:      status,
	}, nil
}

func addTask(tasks *[]*Task, scanner *bufio.Scanner) {
	task, err := getTaskFromUser(scanner)
	if err != nil {
		fmt.Println("Error adding task:", err)
		return
	}
	*tasks = append(*tasks, task)
	fmt.Println("Task added successfully!")
}

func removeTask(tasks *[]*Task, scanner *bufio.Scanner) {
	if len(*tasks) == 0 {
		fmt.Println("Your to-do list is empty.")
		return
	}

	displayTasks(*tasks)

	for {
		fmt.Print("Enter the number of the task you want to remove: ")
		scanner.Scan()
		input := strings.TrimSpace(scanner.Text())
		index, err := strconv.Atoi(input)
		if err != nil || index < 1 || index > len(*tasks) {
			fmt.Println("Invalid task number. Please try again.")
			continue
		}
		removedTask := (*tasks)[index-1]
		*tasks = append((*tasks)[:index-1], (*tasks)[index:]...)
		fmt.Printf("Task removed: %s\n", removedTask)
		break
	}
}

func updateTaskStatus(tasks *[]*Task, archivedTasks *[]*Task, scanner *bufio.Scanner) {
	if len(*tasks) == 0 {
		fmt.Println("Your to-do list is empty.")
		return
	}

	displayTasks(*tasks)

	for {
		fmt.Print("Enter the number of the task you want to update: ")
		scanner.Scan()
		input := strings.TrimSpace(scanner.Text())
		index, err := strconv.Atoi(input)
		if err != nil || index < 1 || index > len(*tasks) {
			fmt.Println("Invalid task number. Please try again.")
			continue
		}

		fmt.Print("Enter new status (In Progress, On Hold, Complete): ")
		scanner.Scan()
		newStatus := strings.ToLower(strings.TrimSpace(scanner.Text()))
		if newStatus != StatusInProgress && newStatus != StatusOnHold && newStatus != StatusComplete {
			fmt.Println("Invalid status. Please try again.")
			continue
		}

		task := (*tasks)[index-1]
		task.Status = newStatus
		if newStatus == StatusComplete {
			*archivedTasks = append(*archivedTasks, task)
			*tasks = append((*tasks)[:index-1], (*tasks)[index:]...)
			fmt.Printf("Task archived: %s\n", task)
		} else {
			fmt.Printf("Task updated: %s\n", task)
		}
		break
	}
}

func displayTasks(tasks []*Task) {
	if len(tasks) == 0 {
		fmt.Println("Your to-do list is empty.")
		return
	}

	fmt.Println("Your to-do list:")
	for i, task := range tasks {
		taskStr := fmt.Sprintf("%d. %s", i+1, task)
		if task.IsOverdue() {
			fmt.Printf("\033[31m%s (OVERDUE)\033[0m\n", taskStr)
		} else if task.DueWithinOneDay() {
			fmt.Printf("\033[33m%s (DUE SOON)\033[0m\n", taskStr)
		} else {
			fmt.Println(taskStr)
		}
	}
}

func displayArchivedTasks(archivedTasks []*Task) {
	if len(archivedTasks) == 0 {
		fmt.Println("No archived tasks.")
		return
	}

	fmt.Println("Archived tasks:")
	for i, task := range archivedTasks {
		fmt.Printf("%d. %s\n", i+1, task)
	}
}

func checkOverdueTasks(tasks []*Task) {
	overdueTasks := []*Task{}
	for _, task := range tasks {
		if task.IsOverdue() {
			overdueTasks = append(overdueTasks, task)
		}
	}

	if len(overdueTasks) > 0 {
		fmt.Println("\nOverdue tasks:")
		for _, task := range overdueTasks {
			fmt.Printf("\033[31m- %s\033[0m\n", task)
		}
		fmt.Println()
	}
}

func saveTasks(tasks []*Task, archivedTasks []*Task, filename string) error {
	data := map[string][]*Task{
		"active":   tasks,
		"archived": archivedTasks,
	}

	file, err := os.Create(filename)
	if err != nil {
		return err
	}
	defer file.Close()

	encoder := json.NewEncoder(file)
	return encoder.Encode(data)
}

func loadTasks(filename string) ([]*Task, []*Task, error) {
	file, err := os.Open(filename)
	if err != nil {
		if os.IsNotExist(err) {
			return []*Task{}, []*Task{}, nil
		}
		return nil, nil, err
	}
	defer file.Close()

	var data map[string][]*Task
	decoder := json.NewDecoder(file)
	err = decoder.Decode(&data)
	if err != nil {
		return nil, nil, err
	}

	return data["active"], data["archived"], nil
}

func main() {
	tasks, archivedTasks, err := loadTasks("my_new_tasks.json")
	if err != nil {
		fmt.Println("Error loading tasks:", err)
		tasks = []*Task{}
		archivedTasks = []*Task{}
	}

	scanner := bufio.NewScanner(os.Stdin)

	checkOverdueTasks(tasks)

	for {
		fmt.Println("\nEnter 'A' to add a task, 'R' to remove a task, 'U' to update task status,")
		fmt.Println("'D' to display tasks, 'V' to view archived tasks, or 'Q' to quit:")
		scanner.Scan()
		choice := strings.ToUpper(strings.TrimSpace(scanner.Text()))

		switch choice {
		case "A":
			addTask(&tasks, scanner)
		case "R":
			removeTask(&tasks, scanner)
		case "U":
			updateTaskStatus(&tasks, &archivedTasks, scanner)
		case "D":
			displayTasks(tasks)
		case "V":
			displayArchivedTasks(archivedTasks)
		case "Q":
			err := saveTasks(tasks, archivedTasks, "my_new_tasks.json")
			if err != nil {
				fmt.Println("Error saving tasks:", err)
			} else {
				fmt.Println("Tasks saved. Goodbye!")
			}
			return
		default:
			fmt.Println("Invalid choice. Please try again.")
		}
	}
}
