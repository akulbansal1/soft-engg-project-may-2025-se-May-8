import React, { useState } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Pencil, Trash2, PlusCircle } from "lucide-react";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
  DialogFooter,
} from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";

interface Contact {
  name: string;
  relation: string;
  phone: string;
}

const EmergencyContactsPage: React.FC = () => {
  const [contacts, setContacts] = useState<Contact[]>([
    { name: "John Doe", relation: "Brother", phone: "+91-9876543210" },
    { name: "Jane Smith", relation: "Neighbor", phone: "+91-9123456780" },
  ]);
  const [modalOpen, setModalOpen] = useState(false);
  const [editIndex, setEditIndex] = useState<number | null>(null);
  const [form, setForm] = useState<Contact>({
    name: "",
    relation: "",
    phone: "",
  });

  const handleOpen = (idx: number | null = null) => {
    if (idx !== null) setForm(contacts[idx]);
    else setForm({ name: "", relation: "", phone: "" });
    setEditIndex(idx);
    setModalOpen(true);
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setForm((prev) => ({ ...prev, [name]: value }));
  };

  const handleSave = () => {
    if (editIndex !== null) {
      const updated = [...contacts];
      updated[editIndex] = form;
      setContacts(updated);
    } else {
      setContacts([...contacts, form]);
    }
    setModalOpen(false);
  };

  const handleDelete = (idx: number) => {
    const updated = contacts.filter((_, i) => i !== idx);
    setContacts(updated);
  };

  return (
    <div className="h-full min-h-[calc(100dvh-110px)] flex flex-col space-y-6">
      <div className="flex justify-between items-center">
        <h2 className="text-xl font-semibold">Emergency Contacts</h2>
        <Button
          onClick={() => handleOpen()}
          className="hover:cursor-pointer"
          variant="outline"
        >
          <PlusCircle /> Add Contact
        </Button>
      </div>

      <ScrollArea className="flex-grow">
        <Card>
          <CardHeader>
            <CardTitle>Contacts List</CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            {contacts.map((contact, idx) => (
              <div
                key={idx}
                className="flex justify-between items-center border-b pb-2"
              >
                <div>
                  <p className="font-medium">
                    {contact.name} ({contact.relation})
                  </p>
                  <p className="text-sm text-muted-foreground">
                    {contact.phone}
                  </p>
                </div>
                <div className="flex space-x-2">
                  <Button
                    variant="ghost"
                    size="icon"
                    className="hover:cursor-pointer"
                    onClick={() => handleOpen(idx)}
                  >
                    <Pencil size={16} />
                  </Button>
                  <Button
                    variant="destructive"
                    size="icon"
                    className="hover:cursor-pointer"
                    onClick={() => handleDelete(idx)}
                  >
                    <Trash2 size={16} />
                  </Button>
                </div>
              </div>
            ))}
          </CardContent>
        </Card>
      </ScrollArea>

      <Dialog open={modalOpen} onOpenChange={setModalOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>
              {editIndex !== null ? "Edit Contact" : "Add Contact"}
            </DialogTitle>
            <DialogDescription>
              Fill in the emergency contact details.
            </DialogDescription>
          </DialogHeader>
          <div className="space-y-4 py-4">
            <Input
              name="name"
              placeholder="Name"
              value={form.name}
              onChange={handleChange}
            />
            <Input
              name="relation"
              placeholder="Relation"
              value={form.relation}
              onChange={handleChange}
            />
            <Input
              name="phone"
              placeholder="Phone"
              value={form.phone}
              onChange={handleChange}
            />
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setModalOpen(false)}>
              Cancel
            </Button>
            <Button onClick={handleSave}>
              {editIndex !== null ? "Save Changes" : "Add Contact"}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
};

export default EmergencyContactsPage;
