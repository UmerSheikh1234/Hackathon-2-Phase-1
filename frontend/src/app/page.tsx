"use client";

import { useState, useEffect, FormEvent } from 'react';
import { Task, getTasks, createTask, deleteTask, markTaskComplete } from '@/lib/api';

import Chat from '@/components/Chat'; // Import the new Chat component

export default function HomePage() {
  const [tasks, setTasks] = useState<Task[]>([]);
  const [newTaskTitle, setNewTaskTitle] = useState('');

  const fetchTasks = async () => {
    try {
      const fetchedTasks = await getTasks();
      setTasks(fetchedTasks);
    } catch (error) {
      console.error('Error fetching tasks:', error);
    }
  };

  useEffect(() => {
    fetchTasks();
  }, []);

  const handleAddTask = async (e: FormEvent) => {
    e.preventDefault();
    if (!newTaskTitle.trim()) return;
    try {
      await createTask({ title: newTaskTitle });
      setNewTaskTitle('');
      fetchTasks(); // Refetch tasks to show the new one
    } catch (error) {
      console.error('Error creating task:', error);
    }
  };

  const handleToggleComplete = async (taskId: number) => {
    try {
      await markTaskComplete(taskId);
      fetchTasks(); // Refetch tasks to update the status
    } catch (error) {
      console.error('Error toggling task completion:', error);
    }
  };

  const handleDeleteTask = async (taskId: number) => {
    try {
      await deleteTask(taskId);
      fetchTasks(); // Refetch tasks to remove the deleted one
    } catch (error) {
      console.error('Error deleting task:', error);
    }
  };

  return (
    <main className="flex min-h-screen flex-col items-center p-12 bg-gray-900 text-white">
      <div className="z-10 w-full max-w-5xl items-center justify-between font-mono text-sm lg:flex">
        <h1 className="text-4xl font-bold mb-4">Todo App</h1>
      </div>
      
      {/* Render the Chat component */}
      <Chat />

      <div className="w-full max-w-5xl mt-12">
        <h2 className="text-2xl font-bold mb-6 border-t border-gray-700 pt-6">Manual Task List</h2>
        <form onSubmit={handleAddTask} className="flex gap-4 mb-8">
          <input
            type="text"
            value={newTaskTitle}
            onChange={(e) => setNewTaskTitle(e.target.value)}
            placeholder="Add a new task..."
            className="flex-grow p-2 rounded bg-gray-800 border border-gray-700 focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
          <button
            type="submit"
            className="px-4 py-2 bg-blue-600 rounded hover:bg-blue-700 transition-colors"
          >
            Add Task
          </button>
        </form>

        <div className="space-y-4">
          {tasks.length > 0 ? (
            tasks.map((task) => (
              <div
                key={task.id}
                className="flex items-center justify-between p-4 bg-gray-800 rounded-lg border border-gray-700"
              >
                <div className="flex items-center">
                  <button
                    onClick={() => handleToggleComplete(task.id)}
                    className={`w-6 h-6 mr-4 rounded-full border-2 ${
                      task.completed ? 'bg-green-500 border-green-500' : 'border-gray-500'
                    }`}
                  ></button>
                  <span className={task.completed ? 'line-through text-gray-500' : ''}>
                    {task.title}
                  </span>
                </div>
                <button
                  onClick={() => handleDeleteTask(task.id)}
                  className="px-3 py-1 bg-red-600 rounded hover:bg-red-700 transition-colors"
                >
                  Delete
                </button>
              </div>
            ))
          ) : (
            <p className="text-gray-500">No tasks yet. Add one above!</p>
          )}
        </div>
      </div>
    </main>
  );
}