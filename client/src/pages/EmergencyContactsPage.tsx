import React, { useState } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Pencil, Trash2, PlusCircle, Search, ArrowLeft } from "lucide-react";
import {
  Dialog,
  DialogTrigger,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
  DialogFooter,
} from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { useNavigate } from "react-router-dom";
import * as yup from "yup";

const contactSchema = yup.object().shape({
  name: yup.string().required("Name is required"),
  relation: yup.string().required("Relation is required"),
  phone: yup
    .string()
    .required("Phone number is required")
    .matches(/^\d+$/, "Phone number must contain only digits"),
});

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
    { name: "Rajesh Kumar", relation: "Father", phone: "+91-9012345678" },
    { name: "Rajesh Kumar", relation: "Father", phone: "+91-9012345678" },
  ]);
  const [modalOpen, setModalOpen] = useState(false);
  const [editIndex, setEditIndex] = useState<number | null>(null);
  const [form, setForm] = useState<Contact>({
    name: "",
    relation: "",
    phone: "",
  });
  const [formErrors, setFormErrors] = useState<{ [key: string]: string }>({});
  const [searchTerm, setSearchTerm] = useState("");
  const navigate = useNavigate();

  const handleOpen = (idx: number | null = null) => {
    if (idx !== null) setForm(contacts[idx]);
    else setForm({ name: "", relation: "", phone: "" });
    setFormErrors({});
    setEditIndex(idx);
    setModalOpen(true);
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setForm((prev) => ({ ...prev, [name]: value }));
    if (formErrors[name]) setFormErrors((prev) => ({ ...prev, [name]: "" }));
  };

  const handleSave = async () => {
    try {
      await contactSchema.validate(form, { abortEarly: false });
      if (editIndex !== null) {
        const updated = [...contacts];
        updated[editIndex] = form;
        setContacts(updated);
      } else {
        setContacts([...contacts, form]);
      }
      setModalOpen(false);
    } catch (err: any) {
      if (err.inner) {
        const errors: { [key: string]: string } = {};
        err.inner.forEach((e: any) => {
          if (e.path) errors[e.path] = e.message;
        });
        setFormErrors(errors);
      }
    }
  };

  const handleDelete = (idx: number) => {
    setContacts((prev) => prev.filter((_, i) => i !== idx));
  };

  const filteredContacts = contacts.filter(
    (c) =>
      c.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      c.relation.toLowerCase().includes(searchTerm.toLowerCase()) ||
      c.phone.includes(searchTerm)
  );

  return (
    <div className="h-[calc(100dvh-110px)] flex flex-col space-y-6 overflow-hidden">
      <div className="flex justify-between items-center">
        <h2 className="text-2xl font-semibold flex items-center">
          <Button
            variant="ghost"
            size="sm"
            onClick={() => navigate("/home")}
            className="mr-4"
          >
            <ArrowLeft size={20} />
          </Button>
          Emergency Contacts
        </h2>
        <Dialog open={modalOpen} onOpenChange={setModalOpen}>
          <DialogTrigger asChild>
            <Button variant="outline" size="sm">
              <PlusCircle className="mr-2" size={16} /> Add Contact
            </Button>
          </DialogTrigger>
          <DialogContent>
            <DialogHeader>
              <DialogTitle>
                {editIndex !== null ? "Edit Contact" : "Add Contact"}
              </DialogTitle>
              <DialogDescription>
                Fill in the emergency contact details.
              </DialogDescription>
            </DialogHeader>
            <div className="grid gap-4 py-4">
              <div>
                <Input
                  name="name"
                  placeholder="Name"
                  value={form.name}
                  onChange={handleChange}
                />
                {formErrors.name && (
                  <p className="text-xs text-red-500 mt-1">{formErrors.name}</p>
                )}
              </div>
              <div>
                <Input
                  name="relation"
                  placeholder="Relation"
                  value={form.relation}
                  onChange={handleChange}
                />
                {formErrors.relation && (
                  <p className="text-xs text-red-500 mt-1">
                    {formErrors.relation}
                  </p>
                )}
              </div>
              <div>
                <Input
                  name="phone"
                  placeholder="Phone"
                  value={form.phone}
                  onChange={handleChange}
                />
                {formErrors.phone && (
                  <p className="text-xs text-red-500 mt-1">
                    {formErrors.phone}
                  </p>
                )}
              </div>
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

      <Card className="flex-1 flex flex-col overflow-hidden bg-transparent">
        <CardHeader>
          <CardTitle>Contacts ({filteredContacts.length})</CardTitle>
        </CardHeader>
        <CardContent className="flex-1 overflow-hidden">
          <ScrollArea className="h-full pr-4">
            {filteredContacts.length === 0 ? (
              <div className="text-center py-8 text-muted-foreground">
                <p>No matching contacts found.</p>
              </div>
            ) : (
              <div className="space-y-4">
                {filteredContacts.map((contact, idx) => (
                  <Card
                    key={idx}
                    className="p-4"
                  >
                    <div className="flex justify-between items-center">
                      <div>
                        <p className="font-semibold text-lg">{contact.name}</p>
                        <p className="text-sm text-muted-foreground">
                          {contact.relation}
                        </p>
                        <p className="text-sm text-muted-foreground">
                          {contact.phone}
                        </p>
                      </div>
                      <div className="flex space-x-2">
                        <Button
                          variant="ghost"
                          size="icon"
                          onClick={() => handleOpen(idx)}
                        >
                          <Pencil size={16} />
                        </Button>
                        <Button
                          variant="destructive"
                          size="icon"
                          onClick={() => handleDelete(idx)}
                        >
                          <Trash2 size={16} />
                        </Button>
                      </div>
                    </div>
                  </Card>
                ))}
              </div>
            )}
          </ScrollArea>
        </CardContent>
      </Card>
    </div>
  );
};

export default EmergencyContactsPage;
