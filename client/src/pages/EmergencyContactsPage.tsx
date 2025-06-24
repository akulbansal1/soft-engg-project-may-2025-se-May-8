import React, { useState } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Pencil, Trash2, PlusCircle, Search } from "lucide-react";
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
    { name: "Rajesh Kumar", relation: "Father", phone: "+91-9012345678" },
  ]);

  const [modalOpen, setModalOpen] = useState(false);
  const [editIndex, setEditIndex] = useState<number | null>(null);
  const [form, setForm] = useState<Contact>({
    name: "",
    relation: "",
    phone: "",
  });
  const [searchTerm, setSearchTerm] = useState("");

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

  const filteredContacts = contacts.filter(
    (c) =>
      c.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      c.relation.toLowerCase().includes(searchTerm.toLowerCase()) ||
      c.phone.includes(searchTerm)
  );

  return (
    <div className="h-[calc(100dvh-110px)] flex flex-col space-y-6 overflow-hidden">
      <div className="flex justify-between items-end">
        <h2 className="text-2xl font-semibold">Emergency Contacts</h2>
        <Button onClick={() => handleOpen()} variant="outline">
          <PlusCircle className="mr-2" size={16} /> Add Contact
        </Button>
      </div>

      <div className="relative">
        <Search
          className="absolute left-3 top-1/2 -translate-y-1/2 text-muted-foreground"
          size={16}
        />
        <Input
          placeholder="Search contacts..."
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          className="pl-10"
        />
      </div>

      <div className="flex-1 overflow-hidden">
        <ScrollArea className="h-full">
          <Card className="w-full">
            <CardHeader>
              <CardTitle>Contacts List</CardTitle>
            </CardHeader>
            <CardContent className="space-y-2">
              {filteredContacts.map((contact, idx) => (
                <div
                  key={idx}
                  className="flex justify-between items-center border-b py-2"
                >
                  <div className="leading-tight">
                    <p className="font-medium text-sm">
                      {contact.name} ({contact.relation})
                    </p>
                    <p className="text-xs text-muted-foreground">
                      {contact.phone}
                    </p>
                  </div>
                  <div className="flex space-x-2">
                    <Button
                      variant="ghost"
                      size="icon"
                      onClick={() => handleOpen(idx)}
                    >
                      <Pencil size={14} />
                    </Button>
                    <Button
                      variant="destructive"
                      size="icon"
                      onClick={() => handleDelete(idx)}
                    >
                      <Trash2 size={14} />
                    </Button>
                  </div>
                </div>
              ))}

              {filteredContacts.length === 0 && (
                <p className="text-center text-muted-foreground py-8">
                  No matching contacts found.
                </p>
              )}
            </CardContent>
          </Card>
        </ScrollArea>
      </div>

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
